from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.xhs.adapter import XHSAdapter
from app.adapters.xhs.normalizer import extract_candidates, fingerprint, normalize_note, normalize_shop
from app.models.account import Account
from app.models.keyword import Keyword, KeywordTask
from app.models.note import Note, NoteSnapshot
from app.models.product import Product, ProductCandidate, ProductMatch
from app.models.raw import RawXhsResponse
from app.models.shop import Shop
from app.models.task import TaskRun
from app.notification.service import default_provider
from app.services.matcher import match_score
from app.services.scoring_service import hot_score


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def persist_raw(db: AsyncSession, endpoint: str, params: dict, payload) -> RawXhsResponse | None:
    from app.adapters.xhs.redact import redact

    row = RawXhsResponse(endpoint=endpoint, request_params=redact(params), response_json=redact(payload))
    db.add(row)
    await db.flush()
    return row


async def upsert_note(db: AsyncSession, raw: dict) -> tuple[Note, bool]:
    data = normalize_note(raw)
    if not data.get("source_note_id"):
        raise ValueError("note missing source_note_id")
    existing = await db.scalar(select(Note).where(Note.source == "xhs", Note.source_note_id == data["source_note_id"]))
    created = existing is None
    note = existing or Note(source="xhs", source_note_id=data["source_note_id"])
    for key in ("title", "content", "note_url", "author_id", "author_name", "like_count", "collect_count", "comment_count", "share_count"):
        setattr(note, key, data.get(key))
    score, grade = hot_score(
        like_velocity=data.get("like_count"),
        collect_velocity=data.get("collect_count"),
        comment_velocity=data.get("comment_count"),
        engagement_rate=None,
        account_baseline=None,
    )
    note.hot_score = score
    note.hot_grade = grade
    db.add(note)
    await db.flush()
    db.add(
        NoteSnapshot(
            note_id=note.id,
            like_count=note.like_count,
            collect_count=note.collect_count,
            comment_count=note.comment_count,
            share_count=note.share_count,
        )
    )
    return note, created


async def run_keyword_job(db: AsyncSession, keyword: Keyword, adapter: XHSAdapter | None = None) -> KeywordTask:
    adapter = adapter or XHSAdapter()
    task = KeywordTask(keyword_id=keyword.id, started_at=utcnow(), status="running")
    run = TaskRun(job_type="keyword_search", status="running", started_at=utcnow())
    db.add_all([task, run])
    await db.flush()
    try:
        notes = await adapter.search_notes_some(keyword.keyword, keyword.fetch_count)
        await persist_raw(db, "note.search-some", {"query": keyword.keyword}, notes)
        new_notes = 0
        for raw in notes:
            note, created = await upsert_note(db, raw)
            if created:
                new_notes += 1
                for cand in extract_candidates((note.title or "") + " " + (note.content or ""), note.source_note_id):
                    row = ProductCandidate(**cand)
                    db.add(row)
                    await db.flush()
                    if cand.get("product_name"):
                        product = Product(
                            source="xhs",
                            product_name=cand.get("product_name"),
                            brand=cand.get("brand"),
                            fingerprint=fingerprint(cand.get("brand"), cand.get("product_name"), None, None),
                            current_price=cand.get("price"),
                            status="NEW",
                        )
                        db.add(product)
        task.fetched = len(notes)
        task.new_notes = new_notes
        task.status = "success"
        task.ended_at = utcnow()
        run.status = "success"
        run.fetched = len(notes)
        run.created_count = new_notes
        run.ended_at = utcnow()
        await db.commit()
        return task
    except Exception as exc:  # noqa: BLE001
        task.status = "failed"
        task.error = str(exc)
        task.ended_at = utcnow()
        run.status = "failed"
        run.error = str(exc)
        run.ended_at = utcnow()
        await db.commit()
        raise


async def run_account_job(db: AsyncSession, account: Account, adapter: XHSAdapter | None = None) -> None:
    adapter = adapter or XHSAdapter()
    if account.source != "pc":
        raise ValueError("account ingest only supports source=pc")
    info = await adapter.get_user_info(account.source_user_id)
    await persist_raw(db, "user.info", {"user_id": account.source_user_id}, info)
    if isinstance(info, dict):
        account.nickname = info.get("nickname") or account.nickname
        account.followers = info.get("fans") or info.get("followers") or account.followers
    url = account.profile_url or f"https://www.xiaohongshu.com/user/profile/{account.source_user_id}"
    notes = await adapter.get_user_notes(url)
    for raw in notes:
        await upsert_note(db, raw)
    account.last_checked_at = utcnow()
    await db.commit()


async def match_candidate_to_shops(db: AsyncSession, candidate: ProductCandidate) -> ProductMatch:
    shops = (await db.scalars(select(Shop))).all()
    best = None
    best_score = 0.0
    payload = {"product_name": candidate.product_name, "brand": candidate.brand, "price": candidate.price}
    for shop in shops:
        score = match_score(payload, {"shop_name": shop.shop_name})
        if score > best_score:
            best_score = score
            best = shop
    match = ProductMatch(
        candidate_id=candidate.id,
        target_type="shop",
        shop_id=best.id if best else None,
        match_score=best_score,
        status="matched" if best_score >= 50 else "unmatched",
    )
    candidate.status = match.status
    db.add(match)
    await db.commit()
    return match


async def notify_hot_note(note: Note) -> None:
    if note.hot_score is None or note.hot_score < 80:
        return
    await default_provider().send("🔥 新爆款笔记", f"{note.title or note.source_note_id} score={note.hot_score}")

from typing import Generator

from fastapi import Request

from backend.src.infrastructure.di.container import Container


def get_container(request: Request) -> Generator[Container, None, None]:
    session = request.app.state.db.get_session()
    try:
        yield Container(session)
    finally:
        session.close()

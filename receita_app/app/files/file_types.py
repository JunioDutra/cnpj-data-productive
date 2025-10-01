from typing import NamedTuple
from datetime import datetime

class FileEntity(NamedTuple):
    id: int
    created_at: datetime | None
    path: str
    name: str
    ref: str
    file_size: int
    status: str
    related_at: str | None

    def from_dict(data: dict) -> 'FileEntity':
        return FileEntity(
            id=data.get('id'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            path=data.get('path', ''),
            name=data.get('name', ''),
            ref=data.get('ref', ''),
            file_size=data.get('file_size', 0),
            status=data.get('status', ''),
            related_at=data.get('related_at')
        )

"""Marshmallow схемы для валидации данных."""

from marshmallow import Schema, fields, validate


class TaskSchema(Schema):
    """Схема для представления задачи в ответе API."""

    id = fields.Integer(required=True, dump_only=True)
    title = fields.String(required=True)
    description = fields.String(allow_none=True)
    status = fields.String(
        required=True, validate=validate.OneOf(["pending", "in_progress", "completed"])
    )
    created_at = fields.String(required=True, dump_only=True)


class TaskCreateSchema(Schema):
    """Схема для валидации данных при создании задачи."""

    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True, validate=validate.Length(max=1000))
    status = fields.String(
        load_default="pending", validate=validate.OneOf(["pending", "in_progress", "completed"])
    )


class TaskUpdateSchema(Schema):
    """Схема для валидации данных при обновлении задачи."""

    title = fields.String(allow_none=True, validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True, validate=validate.Length(max=1000))
    status = fields.String(
        allow_none=True, validate=validate.OneOf(["pending", "in_progress", "completed"])
    )

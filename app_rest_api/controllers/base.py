# -*- coding: utf-8 -*-
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from odoo import http
from odoo.models import Model
from werkzeug.exceptions import BadRequest, MethodNotAllowed


def api_view(
    name_model: str,
    fields: Optional[List[str]] = None,
    optional_fields: Optional[List[str]] = None,
    filters: Dict[str, str] = {},
    domain: List = [],
    defaults: Dict[str, Callable] = {},
    actions: Dict[str, List[Tuple[str, list]]] = {},
    kwargs: Dict[str, Any] = {}
):
    model: Model = http.request.env[name_model]
    method: str = http.request.httprequest.method
    id: int = kwargs.pop("id", None)
    fields_to_extract: Union[List[str], str] = kwargs.pop("fields", None)

    if optional_fields is None:
        optional_fields = list(model.fields_get_keys())

    if fields_to_extract:
        if fields:
            all_fields = set(fields + optional_fields)

            if fields_to_extract == "ALL":
                fields = tuple(all_fields)

            elif isinstance(fields_to_extract, list) and not (set(fields_to_extract) - all_fields):
                fields = fields_to_extract

        elif isinstance(fields_to_extract, list):
            fields = fields_to_extract

    if filters:
        extra_domain = [
            (name, filters[name], kwargs[name]) for name in kwargs
            if name in filters and name in fields
        ]
    else:
        extra_domain = []

    if id is None:
        if method == "GET":
            return model.search(domain + extra_domain).read(fields)

        elif method == "POST":
            for value in defaults:
                if value not in kwargs:
                    kwargs[value] = defaults[value]()

            record = model.create([kwargs])

            response_actions = []

            for action, fields in actions.get("POST", []):
                if hasattr(record, action):
                    result = getattr(record, action)()

                    if result:
                        if fields and isinstance(result, dict):
                            result = {
                                k: v for k, v in result.items() if k in fields
                            }
                        response_actions.append(result)

            data, *_ = record.read(fields)

            if response_actions:
                data["response_actions"] = response_actions

            return data

    else:
        query = model.search([("id", "=", id)] + domain, limit=1)

        if query.exists():
            if method in ("GET", "PUT", "PATCH"):
                if method in ("PUT", "PATCH"):
                    query.write(kwargs)
                record, *_ = query.read(fields)
                return record
        else:
            raise BadRequest()

    raise MethodNotAllowed()


def get_select_options(model_name: str, attribute: str) -> dict:
    return dict(
        http.request.env[model_name].fields_get(
            [attribute]
        )[attribute]["selection"]
    )

"""
Сообщения об ошибках iiko для конечного пользователя (TMA и др.).
Сырой текст из API хранится в Order.error_message; здесь — короткий понятный текст.
"""
import re
from typing import Optional

# Маркеры начала stack trace в ответах .NET / iiko
_STACK_MARKERS = (
    "Server stack trace:",
    "Exception rethrown",
    "\n   в ",  # русская «в» — типичный стек .NET
)


def strip_iiko_stack_trace(raw: str) -> str:
    """Отрезает stack trace, оставляя первую осмысленную часть."""
    if not raw:
        return ""
    text = raw
    cut = len(text)
    for marker in _STACK_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    return text[:cut].strip()


def iiko_error_message_for_user(raw: Optional[str]) -> Optional[str]:
    """
    Преобразует сырое сообщение iiko в одно короткое сообщение для клиента.
    Если шаблон неизвестен — возвращает первую строку без стека (обрезанную).
    """
    if not raw:
        return None

    text = strip_iiko_stack_trace(raw)
    if not text:
        return None

    # Resto.Front.Api: нельзя добавить неактивный товар
    if "CannotAddInactiveProductException" in raw or (
        "is inactive" in text.lower() and "only active products" in text.lower()
    ):
        m = re.search(r'Product\s+"([^"]+)"', text)
        name = m.group(1).strip() if m else None
        if name:
            return (
                f"Позиция «{name}» в ресторане снята с продажи. "
                "Соберите корзину заново без неё и оформите заказ повторно."
            )
        return (
            "В заказе есть позиция, которая в ресторане недоступна для заказа. "
            "Соберите корзину заново без этой позиции и оформите заказ снова."
        )

    # Одна строка / короткий абзац без технической простыни
    first = text.split("\n")[0].strip()
    if len(first) > 240:
        first = first[:237] + "…"
    return first or None

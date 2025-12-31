from typing import Dict, Callable
import asyncio

from aiogram.fsm.context import FSMContext


def sync_make_update_progress(loop, state: FSMContext) -> Callable:
    """
    Возвращает функцию для отслеживания синхроноого прогресса скачивания.

    Args:
        loop (_type_): Цикл событий
        state (FSMContext): Состояние В FSM для обновления прогресса
    """

    def update_progress(
        data_state: bool = None,
    ) -> True:
        data: Dict = asyncio.run_coroutine_threadsafe(state.get_data(), loop).result()
        asyncio.run_coroutine_threadsafe(
            state.update_data(counter_progress=data.get("counter_progress", 0) + 1),
            loop,
        ).result()

        # Дополнительная опция для необходимого состояния
        if data_state:
            asyncio.run_coroutine_threadsafe(
                state.update_data(data_state=data_state),
                loop,
            ).result()

        return True

    return update_progress


def async_make_update_progress(state: FSMContext):
    """
    Фабрика асинхронной функции для обновления прогресса операции в FSM.

    Возвращаемая функция предназначена для многократного вызова во время
    длительной асинхронной операции (например, скачивания или обработки данных)
    и управляет состоянием FSM.

    Контракт FSM:
        - cancel (bool | None):
            Если установлен в True, возвращаемая функция завершает работу
            и возвращает False.
        - counter_progress (int):
            Счётчик прогресса. Увеличивается на 1 при каждом успешном вызове.
        - data_state (Any | None):
            При передаче параметра data_state значение сохраняется в FSM.

    Args:
        state (FSMContext): Контекст FSM для хранения состояния прогресса.

    Returns:
        Callable[[Any | None], Awaitable[bool]]:
            Асинхронная функция update_progress(data_state=None),
            возвращающая:
                - True — если обновление прошло успешно
                - False — если операция была отменена через FSM
    """

    async def update_progress(data_state=None):
        data: Dict = await state.get_data()

        if data.get("cancel"):
            return False

        await state.update_data(counter_progress=data.get("counter_progress", 0) + 1)

        if data_state is not None:
            await state.update_data(data_state=data_state)

        return True

    return update_progress

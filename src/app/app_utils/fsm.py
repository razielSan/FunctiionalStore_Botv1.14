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
    Возвращает функцию для отслеживания асинхронного прогресса скачивания.

    Поддерживает состояние FSM:

    FSM.cancel - Если при вызове функции в FSM.cancel будет какое то значение то
    вернет False
    FSM.counter_progress - каждый раз при вызове функции, counter_progress будет
    увеличен на 1
    FSM.data_state - При указании параметра data_state.Значение парметра будет 
    добавлено в FSM


    Args:
        loop (_type_): Цикл событий
        state (FSMContext): Состояние В FSM для обновление прогресса
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

# starlette — Execução de tarefas em segundo plano

Trecho parcial temporário do modelo, revisado. Contratos importantes continuam sem documentação. Sem aprovação de publicação; citações do código e evidências completas da revisão ficam preservadas separadamente.

Revisão de origem: `271c277da0ff64e2048a4d46ecc812b9d61db5f6`.

## 1

A classe BackgroundTask é usada para executar uma função assíncronamente, com a opção de executá-la em uma fila de threads se não for assíncrona.

Fonte: `starlette/background.py:12`; SHA-256: `0fe5e952915181406765e035b4783330e82e6dee8809564594e03830bd2ad53f`.

    class BackgroundTask:
        def __init__(self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.is_async = is_async_callable(func)
    
        async def __call__(self) -> None:
            if self.is_async:
                await self.func(*self.args, **self.kwargs)
            else:
                await run_in_threadpool(self.func, *self.args, **self.kwargs)
    
    
    class BackgroundTasks(BackgroundTask):
        def __init__(self, tasks: Sequence[BackgroundTask] | None = None):
            self.tasks = list(tasks) if tasks else []
    
        def add_task(self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:
            task = BackgroundTask(func, *args, **kwargs)
            self.tasks.append(task)
    
        async def __call__(self) -> None:
            for task in self.tasks:
                await task()



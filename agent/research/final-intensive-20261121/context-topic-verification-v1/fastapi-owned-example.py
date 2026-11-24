async def resolve_selected(request, dependant, stack, embed_body_fields):
    return await solve_dependencies(
        request=request,
        dependant=dependant,
        async_exit_stack=stack,
        embed_body_fields=embed_body_fields,
    )

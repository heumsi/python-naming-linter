class ObjectContext:
    pass


class MyService:
    object_context: ObjectContext  # pass: matches type
    repo: ObjectContext  # violation: should be object_context

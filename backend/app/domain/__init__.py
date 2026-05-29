"""Business logic modules.

Domain functions take a db session and ORM objects/primitives — never HTTP
Request/Response. They raise DomainError subclasses; routers and exception
handlers translate those to HTTP. This is what lets the scheduler reuse the
same functions as the routes.
"""

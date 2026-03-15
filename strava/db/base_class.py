from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    pass

    # Generate __tablename__ automatically
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

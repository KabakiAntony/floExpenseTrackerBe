from app.api.model import db, ma


class Expense(db.Model):
    """expense model"""
    __tablename__ = "Expense"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expense_sys_id = db.Column(db.String(25), unique=True, nullable=False)
    expense_for = db.Column(db.String(25), nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    expense_client = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.Date, nullable=False)

    def __init__(self, exp_id, exp_for, purpose, exp_client, amt, exp_date):
        self.expense_sys_id = exp_id
        self.expense_for = exp_for
        self.purpose = purpose
        self.expense_client = exp_client
        self.amount = amt
        self.expense_date = exp_date


class ExpenseSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "expense_sys_id", "expense_for",
            "purpose", "expense_client", "amount",
            "expense_date"
            )


expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)

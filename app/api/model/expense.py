from app.api.model import db, ma


class Expense(db.Model):
    """sales model"""
    __tablename__ = "Sale"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expense_sys_id = db.Column(db.String(25), unique=True, nullable=False)
    expense_origin = db.Column(db.String(25), db.ForeignKey('User.user_sys_id'))
    purpose = db.Column(db.String(255), nullable=False)
    expense_client = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
   
    def __init__(self, exp_id, exp_origin, purpose, exp_client, amt, exp_date):
        self.expense_sys_id = exp_id
        self.expense_origin = exp_origin
        self.purpose = purpose
        self.expense_client = exp_client
        self.amount = amt
        self.expense_date = exp_date      


class ExpenseSchema(ma.Schema):
    class Meta:
        fields = (
            "expense_sys_id", "expense_origin",
            "purpose", "expense_client", "amount",
            "expense_date"
            )


sale_schema = ExpenseSchema()
sales_schema = ExpenseSchema(many=True)

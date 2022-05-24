from flask import Flask, render_template, redirect, request, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///all_items.db'

db = SQLAlchemy(app)


class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_number = db.Column(db.String(11), nullable=False, unique=True)
    item_name = db.Column(db.String(200))
    item_count = db.Column(db.Integer, default=0)
    barcode = db.Column(db.LargeBinary)

    def __repr__(self):
        return '<Item %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST' and request.form['item_number']:
        number = request.form['item_number']
        count = int(request.form['item_count']
                    ) if request.form['item_count'] else 0
        name = request.form['item_name']
        new_item = Items(item_number=number, item_count=count, item_name=name)

        try:
            db.session.add(new_item)
            db.session.commit()
            return redirect('/')
        except IntegrityError:
            db.session.rollback()
            items = Items.query.all()
            return render_template('edit.html', items=items)
        except:
            db.session.rollback()
            return '<h1>There was a problem adding this item!</h1>'
    else:
        items = Items.query.all()
        return render_template('index.html', items=items)


@app.route('/delete/<int:id>')
def delete(id: int):
    item_to_delete = Items.query.get_or_404(id)

    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting the item"


@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id: int):
    if request.method == 'POST' and request.form['item_number']:
        number = request.form['item_number']
        count = int(request.form['item_count']
                    ) if request.form['item_count'] else 0
        name = request.form['item_name']
        i = Items.query.get_or_404(id)
        i.item_number, i.item_count, i.item_name = number, count, name
    try:
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem updating the item number'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)

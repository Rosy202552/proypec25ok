from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Estudiante
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estudiantes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-change-in-production'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    estudiantes = Estudiante.query.all()
    return render_template('index.html', estudiantes=estudiantes)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        matricula = request.form['matricula'].strip()
        nombre = request.form['nombre'].strip()
        grupo = request.form['grupo'].strip()

        # Validar duplicado antes de intentar insertar
        existente = Estudiante.query.filter_by(matricula=matricula).first()
        if existente:
            flash('La matrícula ya existe.', 'error')
            # Re-render con los valores ingresados para que el usuario los corrija
            return render_template('add.html', matricula=matricula, nombre=nombre, grupo=grupo)

        nuevo = Estudiante(matricula=matricula, nombre=nombre, grupo=grupo)
        db.session.add(nuevo)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('No se pudo guardar el estudiante: matrícula duplicada.', 'error')
            return render_template('add.html', matricula=matricula, nombre=nombre, grupo=grupo)
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {e}', 'error')
            return render_template('add.html', matricula=matricula, nombre=nombre, grupo=grupo)

        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    estudiante = Estudiante.query.get_or_404(id)
    if request.method == 'POST':
        nueva_matricula = request.form['matricula'].strip()
        nombre = request.form['nombre'].strip()
        grupo = request.form['grupo'].strip()

        # Si la matrícula cambia, comprobar que no pertenezca a otro estudiante
        if nueva_matricula != estudiante.matricula:
            otro = Estudiante.query.filter_by(matricula=nueva_matricula).first()
            if otro and otro.id != estudiante.id:
                flash('La matrícula indicada pertenece a otro estudiante.', 'error')
                return render_template('edit.html', estudiante=estudiante)

        estudiante.matricula = nueva_matricula
        estudiante.nombre = nombre
        estudiante.grupo = grupo
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('No se pudo actualizar: conflicto de matrícula.', 'error')
            return render_template('edit.html', estudiante=estudiante)
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {e}', 'error')
            return render_template('edit.html', estudiante=estudiante)

        return redirect(url_for('index'))
    return render_template('edit.html', estudiante=estudiante)

@app.route('/delete/<int:id>')
def delete(id):
    estudiante = Estudiante.query.get_or_404(id)
    db.session.delete(estudiante)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
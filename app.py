from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import select,extract
from datetime import timedelta,datetime
from dotenv import load_dotenv
from models import db_session, Usuario, Tutor, Pet ,Agendamento
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Tempo máximo de login: 30 minutos
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Configuração do Flask-Login (Requisito 4 e 5)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Faça login para acessar o sistema."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return db_session.get(Usuario, int(user_id))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        usuario = db_session.execute(select(Usuario).where(Usuario.email == email)).scalar()

        if usuario and usuario.check_password(senha):
            session.permanent = True
            login_user(usuario)
            return redirect(url_for('dashboard'))
        else:
            # Requisito 4.1: Informar motivo da falha
            flash('Falha na autenticação: E-mail ou senha incorretos.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()  # Requisito 5.1.2
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    # Renderiza tela com links para Produtos e Estoque e mostra current_user.nome (5.1.1)
    return render_template('dashboard.html')

@app.route('/pet', methods=['GET', 'POST'])
@login_required
def pet():
    termo = request.form.get('busca','')
    if termo:
        busca_pets = (select(Pet)
                         .where(Pet.placa.ilike(f'%{termo}%')))

    else:
        busca_pets = select(Pet)
    pets= db_session.execute(busca_pets).scalars().all()

    return render_template(
        'pets.html',
        pets=pets)


@app.route('/pet/novo', methods=['GET', 'POST'])
@login_required
def pet_novo():
    tutores = db_session.execute(
        select(Tutor)
    ).scalars().all()

    if request.method == 'POST':
        nome = request.form.get('nome')
        raca = request.form.get('raca')
        especie = request.form.get('especie')
        data_nascimento = request.form.get('data_nascimento')
        tutor_id = request.form.get('tutor_id')

        try:
            pet = Pet(
                nome=nome,
                raca=raca,
                especie=especie,
                data_nascimento=data_nascimento,
                tutor_id=int(tutor_id)
            )

            db_session.add(pet)
            db_session.commit()

            flash('Pet cadastrado com sucesso!', 'success')

            return redirect(url_for('pet_novo'))

        except Exception:
            db_session.rollback()
            flash('Erro ao cadastrar pet. Verifique os dados do pet.', 'danger')

    return render_template(
        'pet_novo.html',
        tutores=tutores
    )

@app.route('/tutor', methods=['GET', 'POST'])
@login_required
def tutor():
    termo = request.form.get('busca','')
    if termo:
        busca_tutores = (select(Tutor)
                         .where(Tutor.nome.ilike(f'%{termo}%')))

    else:
        busca_tutores = select(Tutor)
    tutores= db_session.execute(busca_tutores).scalars().all()

    return render_template(
        'tutor.html',
        tutores=tutores)

@app.route('/tutor/novo', methods=['GET', 'POST'])
@login_required
def tutor_novo():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        cpf = request.form['cpf']

        # Validar CPF
        if not Tutor.validar_formato_cpf(cpf):
            flash('CPF inválido!')
            return redirect(url_for('tutor_novo'))
        try:
            novo = Tutor(
                nome=nome,
                telefone=telefone,
            )

            novo.set_cpf(cpf)

            db_session.add(novo)
            db_session.commit()

            flash('Proprietário cadastrado com sucesso!')

            return redirect(url_for('tutor'))
        except Exception as e:
            db_session.rollback()
            flash("Erro ao cadastrar", 'danger')
            return redirect(url_for('tutor_novo'))

    return render_template('tutor_novo.html')

@app.route('/tutor/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def tuto_editar(id):
    tutor = db_session.get(Tutor, id)
    if not tutor:
        flash('Tutor não encontrado!')
        return redirect(url_for('tutor'))

    nome = request.form.get('nome')
    telefone = request.form.get('telefone')

    cpf = request.form.get('cpf')

    if request.method == 'POST':
        try:
            if nome != tutor.nome:
                tutor.nome = nome
            if telefone != tutor.telefone:
                tutor.telefone = telefone
            if cpf:
                tutor.set_cpf(cpf)

            db_session.commit()

            flash('Tutor atualizado com sucesso!')
            return redirect(url_for('tutor'))
        except ValueError as e:
            flash(f"{e}")
            db_session.rollback()
            return redirect(url_for('tutor_editar', id=id))

        except Exception as e:
            db_session.rollback()
            print(e)
            flash('Erro ao atualizar tutor!')
            return redirect(url_for('tutor_editar', id=id))

    return render_template(
        'tutor_editar.html',
        tutor=tutor
    )

@app.route('/tutor/excluir/<int:id>', methods=['POST'])
@login_required
def tutor_excluir(id):
    tutor = db_session.get(Tutor, id)

    if not tutor:
        flash('Proprietário não encontrado!', 'danger')
        return redirect(url_for('proprietario'))

    # Verifica se o tutor possui animais
    if tutor.pets_join:
        flash('Não é possível excluir este tutor, pois ele possui carros cadastrados!', 'warning')
        return redirect(url_for('tutor'))

    try:
        db_session.delete(tutor)
        db_session.commit()

        flash('Proprietário excluído com sucesso!', 'success')

    except Exception as e:
        db_session.rollback()
        print(e)
        flash('Erro ao excluir tutor!', 'danger')

    return redirect(url_for('tutor'))

@app.route('/agendamentos', methods=['GET'])
@login_required
def agendamentos():
    agendamentos = db_session.execute(
        select(Agendamento).order_by(
            extract('day', Agendamento.data_hora).asc())
    ).scalars().all()
    print(agendamentos)

    return render_template('agendamentos.html', agendamentos=agendamentos)

@app.route('/agendamentos/atualizar/<int:id>', methods=['GET', 'POST'])
@login_required
def agendamento_atualizar(id):
    agendamento = db_session.get(Agendamento, id)
    if not agendamento:
        flash('Agendamento não encontrado!')
        return redirect(url_for('agendamentos'))
    if request.method == 'POST':
        data_hora_html = request.form.get('data_hora')  # Ex: "2026-11-10T14:00"
        try:
            # 1. Convertemos a string do HTML num Objeto Datetime
            data_hora_obj = datetime.strptime(data_hora_html, '%Y-%m-%dT%H:%M')

            if data_hora_obj == agendamento.data_hora:
                flash("Mesmo horario de Agendamento")
                return redirect(url_for('agendamentos'))


            # 2. Regra de Negócio: Horário Comercial (08h às 18h)
            if data_hora_obj.hour < 8 or data_hora_obj.hour >= 18:
                flash("A oficina só funciona das 08:00 às 18:00.", "warning")
                return redirect(url_for('agendamentos'))

            # 3. Regra de Negócio: Horas Cheias
            if data_hora_obj.minute != 0:
                flash("Agendamentos apenas em horas exatas (Ex: 14:00).", "warning")
                return redirect(url_for('agendamentos'))

            # 4. REGRA DE CONFLITO (Agora buscando direto pelo objeto DateTime!)
            # O banco compara objetos de tempo de forma nativa e ultra rápida
            stmt_conflito = select(Agendamento).where(Agendamento.data_hora == data_hora_obj)
            horario_ocupado = db_session.execute(stmt_conflito).first()

            if horario_ocupado is not None:
                flash("Este horário já está reservado!", "danger")
                return redirect(url_for('agendamentos'))

            # 5. SALVAMENTO (Enviamos o objeto data_hora_obj direto)
            agendamento.data_hora = data_hora_obj
            db_session.commit()

            flash("Agendamento atualizado com sucesso!", "success")
            return redirect(url_for('agendamentos'))

        except ValueError:
            flash("Formato de data inválido.", "danger")
            return redirect(url_for('agendamentos'))
        except Exception as e:
            db_session.rollback()
            print(f"Erro: {e}")
            flash("Erro interno ao salvar.", "danger")
            return redirect(url_for('agendamentos'))



    return render_template('agendamento_atualizar.html', agendamento=agendamento)

@app.route('/agendamentos/novo', methods=['GET', 'POST'])
@login_required
def agendamento_novo():
    if request.method == 'POST':
        pet_id = request.form.get('pet_id')
        data_hora_html = request.form.get('data_hora')  # Ex: "2026-11-10T14:00"
        motivo = request.form.get('motivo')

        if not pet_id or not data_hora_html or not motivo:
            flash("Todos os campos são obrigatórios!", "danger")
            return redirect(url_for('novo_agendamento'))

        try:
            # 1. Convertemos a string do HTML num Objeto Datetime
            data_hora_obj = datetime.strptime(data_hora_html, '%Y-%m-%dT%H:%M')

            # 2. Regra de Negócio: Horário Comercial (08h às 18h)
            if data_hora_obj.hour < 8 or data_hora_obj.hour >= 18:
                flash("A oficina só funciona das 08:00 às 18:00.", "warning")
                return redirect(url_for('novo_agendamento'))

            # 3. Regra de Negócio: Horas Cheias
            if data_hora_obj.minute != 0:
                flash("Agendamentos apenas em horas exatas (Ex: 14:00).", "warning")
                return redirect(url_for('novo_agendamento'))

            # 4. REGRA DE CONFLITO (Agora buscando direto pelo objeto DateTime!)
            # O banco compara objetos de tempo de forma nativa e ultra rápida
            stmt_conflito = select(Agendamento).where(Agendamento.data_hora == data_hora_obj)
            horario_ocupado = db_session.execute(stmt_conflito).first()

            if horario_ocupado is not None:
                flash("Este horário já está reservado!", "danger")
                return redirect(url_for('agendamentos'))

            # 5. SALVAMENTO (Enviamos o objeto data_hora_obj direto)
            novo_agendamento = Agendamento(
                pet_id=pet_id,
                data_hora=data_hora_obj,  # Salvando como DateTime real
                motivo=motivo
            )

            db_session.add(novo_agendamento)
            db_session.commit()

            flash("Agendamento criado com sucesso!", "success")
            return redirect(url_for('agendamentos'))

        except ValueError:
            flash("Formato de data inválido.", "danger")
            return redirect(url_for('novo_agendamento'))
        except Exception as e:
            db_session.rollback()
            print(f"Erro: {e}")
            flash("Erro interno ao salvar.", "danger")
            return redirect(url_for('agendamento_novo'))
    # se get
    pets_disponiveis = db_session.execute(select(Pet)).scalars().all()
    return render_template('agendamento_novo.html', pets=pets_disponiveis)

if __name__ == '__main__':
    app.run(debug=True, port=5007, host='0.0.0.0')
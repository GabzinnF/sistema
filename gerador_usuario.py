from models import db_session,Usuario, Tutor, Pet

usuarios = [
    {"nome": "Gabriel Favaro", "email": "gabriel.favaro@gmail.com"},
    {"nome": "Marcia Souza", "email": "marcia.souza@gmail.com"},
    {"nome": "Ludmila Dias", "email": "ludmila.dias@gmail.com"},
]
tutor = [

    {"nome": "Fernando Emanuel", "email": "fernando.emanuel@gmail.com",
     "telefone": "11900000001", "cpf": "123.456.789-09"},
    {"nome": "Laura Batista", "email": "laura.batista@gmail.com",
     "telefone": "11900000002", "cpf": "390.533.447-05"},
    {"nome": "Mario Bros", "email": "mario.bros@gmail.com",
     "telefone": "11900000003", "cpf": "935.411.347-80"},
   

]
pets = [
    {"nome": "Cletinho", "raca": "Vira-Lata", "data_nascimento" : "13/04/2024", "especie" : "cachorro"},
    {"nome": "Toddy", "raca": "Poodle", "data_nascimento" : "25/12/2022", "especie" : "cachorro"},
    {"nome": "Guto", "raca": "Shih Tzu" , "data_nascimento": "14/11/2020", "especie" : "cachorro"},
]
"""

    
    
    """


def criar_usuarios():
    for p in usuarios:
        admin = Usuario(
            name=p['nome'],
            email=p['email']
        )
        admin.set_password("@123")

        db_session.add(admin)
        db_session.commit()
        print("criado com sucesso!!!")

def criar_tutores():
    for p in tutor:
        tutor_ = Tutor(
            nome=p['nome'],
            telefone=p['telefone']
        )
        print(tutor_.nome,tutor_.telefone, p['cpf'])
        tutor_.set_cpf(p['cpf'])
        #print(pro_.nome, pro_.email, pro_.telefone)

        db_session.add(tutor_)
        db_session.commit()
        print("criado com sucesso!!!")



def criar_pets():
    for p in pets:
        pet_ = Pet(
            nome=p['nome'],
            raca=p['raca'],
            especie=p['especie'],
            data_nascimento=p['data_nascimento']
        )
        print(pet_.nome,pet_.raca, pet_.especie, pet_.data_nascimento)
        #print(pro_.nome, pro_.email, pro_.telefone)

        db_session.add(pet_)
        db_session.commit()
        print("criado com sucesso!!!")        

criar_tutores()
criar_usuarios()
criar_pets()
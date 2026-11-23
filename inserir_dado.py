
import sqlite3


db = sqlite3.connect('saep_db.db');
db.execute('''INSERT INTO agendamentos 
(data, hora, pet_id) VALUES
 ('2026-11-18 17:00:00.000000', 'Consulta', 1), 
 ('2026-11-18 15:00:00.000000', 'Cirurgia', 2), 
 ('2026-11-18 16:00:00.000000', 'Vacina', 3);''');
db.commit(); db.close(); print('Agendamentos inseridos!')
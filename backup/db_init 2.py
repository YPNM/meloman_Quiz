import mysql.connector as connection
from mysql.connector import Error, IntegrityError, Warning
import config


# Create a decorator that connects to the DB and closes the connection once the function is done
def start_connection():
    # For server use:
    conn = connection.connect(user=config.DB_USER, password=config.DB_PASS,
                              host=config.DB_HOST,
                              database=config.DB_DATABASE)

    cursor = conn.cursor()
    return conn, cursor


def stop_connection(conn, cursor):
    cursor.close()
    conn.close()


def init_db(force=False):
    conn, cursor = start_connection()
    ''' Check that the required cities exist, else create them'''
    ''':param force: Create cities again'''

    if force:
        cursor.execute('DROP TABLE IF EXISTS photos')
        cursor.execute('DROP TABLE IF EXISTS scores')
        cursor.execute('DROP TABLE IF EXISTS rounds')
        cursor.execute('DROP TABLE IF EXISTS teams')
        cursor.execute('DROP TABLE IF EXISTS games')
        cursor.execute('DROP TABLE IF EXISTS game_types')
        cursor.execute('DROP TABLE IF EXISTS seasons')
        cursor.execute('DROP TABLE IF EXISTS cities')

    cursor.execute('''CREATE TABLE IF NOT EXISTS cities (
                        city_id BINARY(16) PRIMARY KEY,
                        city_name VARCHAR(128) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                        '''
                   )

    cursor.execute('''CREATE TABLE IF NOT EXISTS game_types (
                                game_type_id BINARY(16) PRIMARY KEY,
                                game_type_name VARCHAR(128) NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                                '''
                   )

    cursor.execute('''CREATE TABLE IF NOT EXISTS seasons (
                            season_id BINARY(16) PRIMARY KEY,
                            season_name VARCHAR(128) NOT NULL,
                            season_description VARCHAR(128) NOT NULL,
                            preview_photo LONGBLOB,
                            season_time DATETIME,
                            city_id BINARY(16) NOT NULL,
                            FOREIGN KEY (city_id) REFERENCES cities(city_id),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                            '''
                   )

    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                            event_id BINARY(16) PRIMARY KEY,
                            event_name VARCHAR(128) NOT NULL,
                            event_description VARCHAR(128) NOT NULL,
                            cost INT NOT NULL,
                            preview_photo LONGBLOB,
                            event_time DATETIME,
                            published BOOLEAN NOT NULL,
                            booking_link VARCHAR(128) NOT NULL,
                            location VARCHAR(128) NOT NULL,
                            city_id BINARY(16) NOT NULL,
                            FOREIGN KEY (city_id) REFERENCES cities(city_id),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                            '''
                   )

    cursor.execute('''CREATE TABLE IF NOT EXISTS games (
                            game_id BINARY(16) PRIMARY KEY,
                            game_name VARCHAR(128) NOT NULL,
                            game_description VARCHAR(128) NOT NULL,
                            preview_photo LONGBLOB,
                            game_time DATETIME,
                            location VARCHAR(128),
                            published BOOLEAN NOT NULL,
                            score_published BOOLEAN NOT NULL,
                            booking_link VARCHAR(128) NOT NULL,
                            city_id BINARY(16) NOT NULL,
                            FOREIGN KEY (city_id) REFERENCES cities(city_id),
                            season_id BINARY(16) NOT NULL,
                            FOREIGN KEY (season_id) REFERENCES seasons(season_id),
                            game_type_id BINARY(16) NOT NULL,
                            FOREIGN KEY (game_type_id) REFERENCES game_types(game_type_id),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                            '''
                   )


    cursor.execute('''CREATE TABLE IF NOT EXISTS teams (
                                team_id BINARY(16) PRIMARY KEY,
                                team_name VARCHAR(128) NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                                '''
                   )

    cursor.execute('''CREATE TABLE IF NOT EXISTS rounds (
                                round_id BINARY(16) PRIMARY KEY,
                                round_name VARCHAR(128) NOT NULL,
                                game_id BINARY(16) NOT NULL,
                                FOREIGN KEY (game_id) REFERENCES games(game_id),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                                '''
                   )

    cursor.execute('''CREATE TABLE IF NOT EXISTS scores (
                            team_id BINARY(16) NOT NULL,
                            FOREIGN KEY (team_id) REFERENCES teams(team_id),
                            round_id BINARY(16) NOT NULL,
                            FOREIGN KEY (round_id) REFERENCES rounds(round_id),
                            score INT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY(team_id, round_id)
                            ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                            '''
                   )

    cursor.execute('''CREATE TABLE IF NOT EXISTS photos (
                            game_id BINARY(16) NOT NULL,
                            FOREIGN KEY (game_id) REFERENCES games(game_id),
                            preview_photo LONGBLOB,
                            photo_link VARCHAR(128) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                            '''
                   )

    cursor.execute('''CREATE TABLE IF NOT EXISTS item_catalog (
                            item_id BINARY(16) NOT NULL,
                            item_name VARCHAR(128) NOT NULL,
                            item_description VARCHAR(128) NOT NULL,
                            cost INT,
                            preview_photo LONGBLOB,
                            booking_link VARCHAR(128) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

    conn.commit()
    stop_connection(conn, cursor)


def convert_bytes_to_string(turple, fetchone=False):
    result = []
    if(fetchone):
        for item in turple:
            if (isinstance(item, bytearray) or isinstance(item, bytes)):
                item = item.decode()
                result.append(item)
            else:
                result.append(item)
    else:
        for data in turple:
            temp = []
            for item in data:
                if(isinstance(item, bytearray) or isinstance(item, bytes)):
                    item = item.decode()
                    temp.append(item)
                else:
                    temp.append(item)
            result.append(temp)
    return result

class CitiesDB():

    def __init__(self):
        pass

    def is_exists(self, cityName):
        try:
            conn, cursor = start_connection()
            prepared_query = 'SELECT city_name FROM cities WHERE city_name = %s'
            data = (f'{cityName}',)
            cursor.execute(prepared_query, data)
            cursor.fetchall()
            stop_connection(conn, cursor)
            if(cursor.rowcount < 1):
                return True
            elif(cursor.rowcount >= 1):
                return 2
        except Exception as err:
            print(err)
            return 3


    def create_new_city(self, cityName):
        is_exists = self.is_exists(cityName)
        if(is_exists == True):
            conn, cursor = start_connection()
            prepared_query = 'INSERT INTO cities(city_id, city_name) VALUES (UUID_TO_BIN(UUID()),%s)'
            data = (f'{cityName}',)
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        elif(is_exists == 2):
            return 2
        else:
            return 3

    def edit_city_by_id(self, city_id, cityName):
        is_exists = self.is_exists(cityName)
        if (is_exists == True):
            conn, cursor = start_connection()
            prepared_query = 'UPDATE cities SET city_name = %s WHERE city_id = %s'
            data = (f'{cityName}',f'{city_id}',)
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        elif (is_exists == 2):
            return 2
        else:
            return 3

    def get_all_cities(self, city_id=None):
        conn, cursor = start_connection()
        if(city_id):
            prepared_query = 'SELECT BIN_TO_UUID(city_id), city_name FROM cities WHERE city_id = %s'
            data = (f'{city_id}',)
            cursor.execute(prepared_query, data)
        else:
            prepared_query = 'SELECT BIN_TO_UUID(city_id), city_name FROM cities'
            cursor.execute(prepared_query)
        results = cursor.fetchall()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(results)

    def get_city_by_id(self, cityId):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(city_id), city_name FROM cities WHERE city_id = %s'
        data = (f'{cityId}',)
        cursor.execute(prepared_query, data)
        result = cursor.fetchone()
        stop_connection(conn, cursor)
        return result

    def delete_city_by_id(self, cityId):
        conn, cursor = start_connection()
        prepared_query = 'DELETE FROM cities WHERE city_id = %s'
        data = (f'{cityId}',)
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

class SeasonsDB():

    def is_exists(self, seasonId):
        try:
            conn, cursor = start_connection()
            prepared_query = 'SELECT BIN_TO_UUID(season_id) FROM seasons WHERE season_id = %s'
            data = (f'{seasonId}',)
            cursor.execute(prepared_query, data)
            cursor.fetchall()
            stop_connection(conn, cursor)
            if(cursor.rowcount < 1):
                return True
            elif(cursor.rowcount >= 1):
                return 2
        except Exception as err:
            print(err)
            return 3

    def create_new_season(self, seasonName, seasonDescription, cityId, previewPhotoBase64):
        conn, cursor = start_connection()
        prepared_query = 'INSERT INTO seasons(season_id, season_name, season_description, city_id, preview_photo) VALUES (UUID_TO_BIN(UUID()),%s,%s,UUID_TO_BIN(%s),%s)'
        data = (f'{seasonName}', f'{seasonDescription}', f'{cityId}', f'{previewPhotoBase64}')
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

    def edit_season_by_id(self, seasonId, seasonName, seasonDescription, cityId, previewPhotoBase64=None):
        try:
            conn, cursor = start_connection()
            if(previewPhotoBase64 != None):
                prepared_query = 'UPDATE seasons SET season_name = %s, season_description = %s, preview_photo = %s, city_id = %s WHERE season_id = %s'
                data = (f'{seasonName}', f'{seasonDescription}', f'{previewPhotoBase64}', f'{cityId}', f'{seasonId}')

            else:
                prepared_query = 'UPDATE seasons SET season_name = %s, season_description = %s, city_id = %s WHERE season_id = %s'
                data = (f'{seasonName}', f'{seasonDescription}', f'{cityId}', f'{seasonId}')
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        except Exception as err:
            print(err)
            return 3

    def get_all_seasons(self, city_id=None):
        conn, cursor = start_connection()
        if(city_id):
            prepared_query = 'SELECT BIN_TO_UUID(s.season_id), s.season_name, s.season_description, c.city_name, s.preview_photo, BIN_TO_UUID(c.city_id) FROM seasons AS s LEFT JOIN cities AS c ON s.city_id = c.city_id WHERE s.city_id = %s'
            data = (f'{city_id}',)
            cursor.execute(prepared_query, data)
        else:
            prepared_query = 'SELECT BIN_TO_UUID(s.season_id), s.season_name, s.season_description, c.city_name, s.preview_photo, BIN_TO_UUID(c.city_id) FROM seasons AS s LEFT JOIN cities AS c ON s.city_id = c.city_id'
            cursor.execute(prepared_query)
        result = cursor.fetchall()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result)

    def get_season_by_id(self, seasonId):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(s.season_id), s.season_name, s.season_description, BIN_TO_UUID(c.city_id), c.city_name, s.preview_photo FROM seasons AS s LEFT JOIN cities AS c ON s.city_id = c.city_id WHERE season_id = %s'
        data = (f'{seasonId}',)
        cursor.execute(prepared_query, data)
        result = cursor.fetchone()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result, fetchone=True)

    def delete_season_by_id(self, seasonId, city_id=None):
        conn, cursor = start_connection()
        if(city_id):
            prepared_query = 'DELETE FROM seasons WHERE season_id = %s AND city_id = %s'
            data = (f'{seasonId}',f'{city_id}')
        else:
            prepared_query = 'DELETE FROM seasons WHERE season_id = %s'
            data = (f'{seasonId}',)
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

class GamesDB():

    def is_exists(self, gameId):
        try:
            conn, cursor = start_connection()
            prepared_query = 'SELECT BIN_TO_UUID(game_id) FROM games WHERE game_id = %s'
            data = (f'{gameId}',)
            cursor.execute(prepared_query, data)
            cursor.fetchall()
            stop_connection(conn, cursor)
            if(cursor.rowcount < 1):
                return True
            elif(cursor.rowcount >= 1):
                return 2
        except Exception as err:
            print(err)
            return 3

    def create_new_game(self, gameName, gameDescription, gameDate, gameTypeId, location, season_id, city_id, bookingLink, previewPhotoBase64):
        conn, cursor = start_connection()
        prepared_query = 'INSERT INTO games(game_id, game_name, game_description, game_type_id, game_time, location, season_id, city_id, published, score_published, booking_link, preview_photo) VALUES (UUID_TO_BIN(UUID()),%s,%s,UUID_TO_BIN(%s),%s,%s,UUID_TO_BIN(%s),UUID_TO_BIN(%s),%s,%s,%s,%s)'
        data = (f'{gameName}', f'{gameDescription}', f'{gameTypeId}', f'{gameDate}', f'{location}', f'{season_id}', f'{city_id}', False, False, f'{bookingLink}', f'{previewPhotoBase64}')
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

    def edit_game_by_id(self, game_id, gameName, gameDescription, gameTypeId, gameDate, location, season_id, city_id, bookingLink, published, scorePublished, previewPhotoBase64=None):
        try:
            conn, cursor = start_connection()
            if(previewPhotoBase64 != None):
                prepared_query = 'UPDATE games SET game_name = %s, game_description = %s, game_type_id = %s, game_time = %s, location = %s, season_id = %s, city_id = %s, booking_link = %s, published = %s, score_published = %s, preview_photo = %s WHERE game_id = %s'
                data = (f'{gameName}', f'{gameDescription}', f'{gameTypeId}' ,f'{gameDate}', f'{location}', f'{season_id}', f'{city_id}', f'{bookingLink}', published, scorePublished, f'{previewPhotoBase64}', f'{game_id}')

            else:
                prepared_query = 'UPDATE games SET game_name = %s, game_description = %s, game_type_id = %s, game_time = %s, location = %s, season_id = %s, city_id = %s, booking_link = %s, published = %s, score_published = %s WHERE game_id = %s'
                data = (f'{gameName}', f'{gameDescription}', f'{gameTypeId}',f'{gameDate}', f'{location}', f'{season_id}', f'{city_id}', f'{bookingLink}', published, scorePublished, f'{game_id}')
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        except Exception as err:
            print(err)
            return 3

    def get_all_games(self, city_id=None):
        conn, cursor = start_connection()
        if(city_id):
            prepared_query = 'SELECT BIN_TO_UUID(g.game_id), g.game_name, g.game_description, gt.game_type_name, g.game_time, c.city_name, g.location, s.season_name, g.published, g.score_published, g.booking_link, g.preview_photo, BIN_TO_UUID(c.city_id) FROM games AS g LEFT JOIN cities AS c ON g.city_id = c.city_id LEFT JOIN seasons AS s ON s.season_id = g.season_id LEFT JOIN game_types AS gt ON gt.game_type_id = g.game_type_id WHERE g.city_id = %s'
            data = (f'{city_id}',)
            cursor.execute(prepared_query, data)
        else:
            prepared_query = 'SELECT BIN_TO_UUID(g.game_id), g.game_name, g.game_description, gt.game_type_name, g.game_time, c.city_name, g.location, s.season_name, g.published, g.score_published, g.booking_link, g.preview_photo, BIN_TO_UUID(c.city_id) FROM games AS g LEFT JOIN cities AS c ON g.city_id = c.city_id LEFT JOIN seasons AS s ON s.season_id = g.season_id LEFT JOIN game_types AS gt ON gt.game_type_id = g.game_type_id'
            cursor.execute(prepared_query)
        result = cursor.fetchall()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result)

    def get_game_by_id(self, gameId):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(g.game_id), g.game_name, g.game_description, g.game_type_id, gt.game_type_name, g.game_time, BIN_TO_UUID(c.city_id), c.city_name, g.location, BIN_TO_UUID(s.season_id), s.season_name, g.score_published, g.published, g.booking_link, g.preview_photo FROM games AS g LEFT JOIN cities AS c ON g.city_id = c.city_id LEFT JOIN seasons AS s ON s.season_id = g.season_id LEFT JOIN game_types AS gt ON g.game_type_id = gt.game_type_id WHERE g.game_id = %s'
        data = (f'{gameId}',)
        cursor.execute(prepared_query, data)
        result = cursor.fetchone()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result, fetchone=True)

    def delete_game_by_id(self, gameId, city_id=None):
        conn, cursor = start_connection()
        if(city_id):
            prepared_query = 'DELETE FROM games WHERE game_id = %s AND city_id=%s'
            data = (f'{gameId}',f'{city_id}')
        else:
            prepared_query = 'DELETE FROM games WHERE game_id = %s'
            data = (f'{gameId}',)
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

class RoundsDB():

    def admin_permission_check(self, game_id, city_id):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(game_id), BIN_TO_UUID(city_id) FROM games WHERE game_id = %s and city_id = %s and score_published != 1'
        data = (f'{game_id}',f'{city_id}')
        cursor.execute(prepared_query, data)
        result = cursor.fetchall()
        stop_connection(conn, cursor)
        if(cursor.rowcount == 1):
            return True
        else:
            return False


    def create_new_rounds(self, game_id, roundsCount):
        conn, cursor = start_connection()
        print(roundsCount)
        for i in range(1, roundsCount+1):
            prepared_query = 'INSERT INTO rounds(round_id, round_name, game_id) VALUES (UUID_TO_BIN(UUID()),%s,UUID_TO_BIN(%s))'
            data = (f'Раунд {i}', f'{game_id}')
            cursor.execute(prepared_query, data)
            conn.commit()
        stop_connection(conn, cursor)
        return True

    def get_all_rounds(self, game_id):
        conn, cursor = start_connection()
        prepared_query = 'SELECT r.round_id, r.round_name, r.game_id FROM rounds AS r LEFT JOIN games AS g ON g.game_id = r.game_id WHERE r.game_id = %s'
        data = (f'{game_id}',)
        cursor.execute(prepared_query, data)
        result = cursor.fetchall()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result)

    def delete_round_by_id(self, round_id):
        conn, cursor = start_connection()
        prepared_query = 'DELETE FROM rounds WHERE round_id = %s'
        data = (f'{round_id}',)
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

class TeamsDB():

    def __init__(self):
        pass

    def is_exists(self, teamName):
        try:
            conn, cursor = start_connection()
            prepared_query = 'SELECT team_name FROM teams WHERE team_name = %s'
            data = (f'{teamName}',)
            cursor.execute(prepared_query, data)
            cursor.fetchall()
            stop_connection(conn, cursor)
            if(cursor.rowcount < 1):
                return True
            elif(cursor.rowcount >= 1):
                return 2
        except Exception as err:
            print(err)
            return 3


    def create_new_team(self, teamName):
        is_exists = self.is_exists(teamName)
        if(is_exists == True):
            conn, cursor = start_connection()
            prepared_query = 'INSERT INTO teams(team_id, team_name) VALUES (UUID_TO_BIN(UUID()),%s)'
            data = (f'{teamName}',)
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        elif(is_exists == 2):
            return 2
        else:
            return 3

    def edit_team_by_id(self, team_id, teamName):
        is_exists = self.is_exists(teamName)
        if (is_exists == True):
            conn, cursor = start_connection()
            prepared_query = 'UPDATE teams SET team_name = %s WHERE team_id = %s'
            data = (f'{teamName}',f'{team_id}',)
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        elif (is_exists == 2):
            return 2
        else:
            return 3

    def get_all_teams(self):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(team_id), team_name FROM teams'
        cursor.execute(prepared_query)
        results = cursor.fetchall()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(results)

    def get_team_by_id(self, teamId):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(team_id), team_name FROM teams WHERE team_id = %s'
        data = (f'{teamId}',)
        cursor.execute(prepared_query, data)
        result = cursor.fetchone()
        stop_connection(conn, cursor)
        return result

    def delete_team_by_id(self, teamId):
        conn, cursor = start_connection()
        prepared_query = 'DELETE FROM teams WHERE team_id = %s'
        data = (f'{teamId}',)
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

class ScoresDB():
    def add_scores(self, dictionary):
        conn, cursor = start_connection()
        for key, value in dictionary.items():
            if(value != ''):
                key = key.split('/')
                round_id = key[0]
                team_id = key[1]
                prepared_query = 'INSERT INTO scores(team_id, round_id, score) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE score = %s'
                data = (f'{team_id}', f'{round_id}', value, value)
                cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

    def get_scores_by_game_id(self, game_id):
        conn, cursor = start_connection()
        print(game_id)
        prepared_query = 'SELECT BIN_TO_UUID(r.round_id), r.round_name, BIN_TO_UUID(s.team_id), s.score, (SELECT SUM(score) FROM scores WHERE t.team_id = team_id GROUP BY team_id) AS total, t.team_name FROM rounds AS r LEFT JOIN games AS g ON r.game_id = UUID_TO_BIN(g.game_id) LEFT JOIN scores AS s ON s.round_id = r.round_id LEFT JOIN teams AS t ON s.team_id = t.team_id WHERE g.game_id = UUID_TO_BIN(%s) ORDER BY total DESC, r.round_name'
        data = (f'{game_id}',)
        cursor.execute(prepared_query, data)
        results = cursor.fetchall()
        stop_connection(conn, cursor)
        print(results)
        if(results[0][2] != None):
            dictionary = {}
            for result in results:
                if(result[5] not in dictionary.keys()):
                    dictionary[result[5]] = []
                sortedArray = convert_bytes_to_string(result[:5], True)
                dictionary[result[5]].append(sortedArray)
            sortedDict = {}
            dictValues = list(dictionary.values())
            if(dictValues[0][0][4] == dictValues[1][0][4] and dictValues[0][len(dictValues[0])-1][3] < dictValues[1][len(dictValues[1])-1][3]):
                dictKeys = list(dictionary.keys())
                sortedDict[dictKeys[1]] = list(dictionary.values())[1]
                sortedDict[dictKeys[0]] = list(dictionary.values())[0]
                for item in dictKeys[2:]:
                    sortedDict[item] = dictionary[item]
                return sortedDict
            else:
                return dictionary
        else:
            return None


class EventsDB():
    def create_new_event(self, eventName, eventDescription, eventDate, eventCost, location, city_id, bookingLink, previewPhotoBase64):
        conn, cursor = start_connection()
        prepared_query = 'INSERT INTO events(event_id, event_name, event_description, event_time, cost, location, city_id, published, booking_link, preview_photo) VALUES (UUID_TO_BIN(UUID()),%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        data = (f'{eventName}', f'{eventDescription}', f'{eventDate}', f'{eventCost}', f'{location}', f'{city_id}', False, f'{bookingLink}', f'{previewPhotoBase64}')
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

    def edit_event_by_id(self, event_id, eventName, eventDescription, eventDate, eventCost, location, city_id, bookingLink, published, previewPhotoBase64=None):
        try:
            conn, cursor = start_connection()
            if(previewPhotoBase64 != None):
                prepared_query = 'UPDATE events SET event_name = %s, event_description = %s, event_time = %s, location = %s, cost = %s, city_id = %s, booking_link = %s, published = %s, preview_photo = %s WHERE event_id = %s'
                data = (f'{eventName}', f'{eventDescription}', f'{eventDate}', f'{location}', f'{eventCost}', f'{city_id}', f'{bookingLink}', published, f'{previewPhotoBase64}', f'{event_id}')
            else:
                prepared_query = 'UPDATE events SET event_name = %s, event_description = %s, event_time = %s, location = %s, cost = %s, city_id = %s, booking_link = %s, published = %s WHERE event_id = %s'
                data = (f'{eventName}', f'{eventDescription}', f'{eventDate}', f'{location}', f'{eventCost}', f'{city_id}', f'{bookingLink}', published, f'{event_id}')
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        except Exception as err:
            print(err)
            return 3

    def get_all_events(self, city_id=None):
        conn, cursor = start_connection()
        if(city_id):
            prepared_query = 'SELECT BIN_TO_UUID(e.event_id), e.event_name, e.event_description, e.event_time, e.cost, c.city_name, e.location, e.published, e.booking_link, e.preview_photo FROM events AS e LEFT JOIN cities AS c ON e.city_id = c.city_id WHERE e.city_id = %s'
            data = (f'{city_id}',)
            cursor.execute(prepared_query, data)
        else:
            prepared_query = 'SELECT BIN_TO_UUID(e.event_id), e.event_name, e.event_description, e.event_time, e.cost, c.city_name, e.location, e.published, e.booking_link, e.preview_photo FROM events AS e LEFT JOIN cities AS c ON e.city_id = c.city_id'
            cursor.execute(prepared_query)
        result = cursor.fetchall()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result)

    def get_event_by_id(self, eventId):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(e.event_id), e.event_name, e.event_description, e.event_time, e.cost, BIN_TO_UUID(c.city_id), c.city_name, e.location, e.published, e.booking_link, e.preview_photo FROM events AS e LEFT JOIN cities AS c ON e.city_id = c.city_id WHERE event_id = %s'
        data = (f'{eventId}',)
        cursor.execute(prepared_query, data)
        result = cursor.fetchone()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result, fetchone=True)

    def delete_event_by_id(self, eventId):
        conn, cursor = start_connection()
        prepared_query = 'DELETE FROM events WHERE event_id = %s'
        data = (f'{eventId}',)
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

class PhotosDB():

    def create_new_photos(self, game_id, photoLink, previewPhotoBase64):
        conn, cursor = start_connection()
        prepared_query = 'INSERT INTO photos(game_id, photo_link, preview_photo) VALUES (%s,%s,%s)'
        data = (f'{game_id}', f'{photoLink}', f'{previewPhotoBase64}')
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

    def edit_photos_by_id(self, game_id, photoLink, previewPhotoBase64=None):
        try:
            conn, cursor = start_connection()
            if(previewPhotoBase64 != None):
                prepared_query = 'UPDATE photos SET photo_link = %s, preview_photo = %s WHERE game_id = %s'
                data = (f'{photoLink}', f'{previewPhotoBase64}', f'{game_id}')
            else:
                prepared_query = 'UPDATE photos SET photo_link = %s WHERE game_id = %s'
                data = (f'{photoLink}', f'{game_id}')
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        except Exception as err:
            print(err)
            return 3

    def get_all_photos(self, city_id=None):
        conn, cursor = start_connection()
        if(city_id):
            prepared_query = 'SELECT BIN_TO_UUID(g.game_id),g.game_name, p.photo_link, p.preview_photo FROM photos AS p LEFT JOIN games AS g ON p.game_id = g.game_id WHERE g.city_id=%s'
            data = (f'{city_id}',)
            cursor.execute(prepared_query, data)
        else:
            prepared_query = 'SELECT BIN_TO_UUID(g.game_id),g.game_name, p.photo_link, p.preview_photo FROM photos AS p LEFT JOIN games AS g ON p.game_id = g.game_id'
            cursor.execute(prepared_query)
        result = cursor.fetchall()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result)

    def get_photos_by_id(self, game_id):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(g.game_id), g.game_name, p.photo_link, p.preview_photo FROM photos AS p LEFT JOIN games AS g ON g.game_id = p.game_id WHERE p.game_id = %s'
        data = (f'{game_id}',)
        cursor.execute(prepared_query, data)
        result = cursor.fetchone()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result, fetchone=True)

    def delete_photos_by_id(self, gameId):
        conn, cursor = start_connection()
        prepared_query = 'DELETE FROM photos WHERE game_id = %s'
        data = (f'{gameId}',)
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

class GametypesDB():

    def __init__(self):
        pass

    def is_exists(self, gameTypeName):
        try:
            conn, cursor = start_connection()
            prepared_query = 'SELECT game_type_name FROM game_types WHERE game_type_name = %s'
            data = (f'{gameTypeName}',)
            cursor.execute(prepared_query, data)
            cursor.fetchall()
            stop_connection(conn, cursor)
            if(cursor.rowcount < 1):
                return True
            elif(cursor.rowcount >= 1):
                return 2
        except Exception as err:
            print(err)
            return 3


    def create_new_gametype(self, gameTypeName):
        is_exists = self.is_exists(gameTypeName)
        if(is_exists == True):
            conn, cursor = start_connection()
            prepared_query = 'INSERT INTO game_types(game_type_id, game_type_name) VALUES (UUID_TO_BIN(UUID()),%s)'
            data = (f'{gameTypeName}',)
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        elif(is_exists == 2):
            return 2
        else:
            return 3

    def edit_gametype_by_id(self, gameTypeId, gameTypeName):
        is_exists = self.is_exists(gameTypeName)
        if (is_exists == True):
            conn, cursor = start_connection()
            prepared_query = 'UPDATE game_types SET game_type_name = %s WHERE game_type_id = %s'
            data = (f'{gameTypeName}',f'{gameTypeId}',)
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        elif (is_exists == 2):
            return 2
        else:
            return 3

    def get_all_gametypes(self):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(game_type_id), game_type_name FROM game_types'
        cursor.execute(prepared_query)
        results = cursor.fetchall()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(results)

    def get_gametype_by_id(self, gameTypeId):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(game_type_id), game_type_name FROM game_types WHERE game_type_id = %s'
        data = (f'{gameTypeId}',)
        cursor.execute(prepared_query, data)
        result = cursor.fetchone()
        stop_connection(conn, cursor)
        return result

    def delete_gametype_by_id(self, gameTypeId):
        conn, cursor = start_connection()
        prepared_query = 'DELETE FROM game_types WHERE game_type_id = %s'
        data = (f'{gameTypeId}',)
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

class CatalogDB():

    def create_new_item(self, itemName, itemDescription, itemCost, bookingLink, previewPhotoBase64):
        conn, cursor = start_connection()
        prepared_query = 'INSERT INTO item_catalog(item_id, item_name, item_description, cost, booking_link, preview_photo) VALUES (UUID_TO_BIN(UUID()),%s,%s,%s,%s,%s)'
        data = (f'{itemName}', f'{itemDescription}', f'{itemCost}', f'{bookingLink}',f'{previewPhotoBase64}')
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True

    def edit_item_by_id(self, item_id, itemName, itemDescription, itemCost, bookingLink, previewPhotoBase64=None):
        try:
            conn, cursor = start_connection()
            if(previewPhotoBase64 != None):
                prepared_query = 'UPDATE item_catalog SET item_name = %s, item_description=%s, cost=%s, booking_link=%s, preview_photo = %s WHERE item_id = %s'
                data = (f'{itemName}', f'{itemDescription}', f'{itemCost}', f'{bookingLink}', f'{previewPhotoBase64}', f'{item_id}')
            else:
                prepared_query = 'UPDATE item_catalog SET item_name = %s, item_description=%s, cost=%s, booking_link=%s WHERE item_id = %s'
                data = (f'{itemName}', f'{itemDescription}', f'{itemCost}', f'{bookingLink}', f'{item_id}')
            cursor.execute(prepared_query, data)
            conn.commit()
            stop_connection(conn, cursor)
            return True
        except Exception as err:
            print(err)
            return 3

    def get_all_catalog(self):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(item_id), item_name, item_description, cost, booking_link, preview_photo FROM item_catalog'
        cursor.execute(prepared_query)
        result = cursor.fetchall()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result)

    def get_item_by_id(self, item_id):
        conn, cursor = start_connection()
        prepared_query = 'SELECT BIN_TO_UUID(item_id), item_name, item_description, cost, booking_link, preview_photo FROM item_catalog WHERE item_id = %s'
        data = (f'{item_id}',)
        cursor.execute(prepared_query, data)
        result = cursor.fetchone()
        stop_connection(conn, cursor)
        return convert_bytes_to_string(result, fetchone=True)

    def delete_item_by_id(self, itemId):
        conn, cursor = start_connection()
        prepared_query = 'DELETE FROM item_catalog WHERE item_id = %s'
        data = (f'{itemId}',)
        cursor.execute(prepared_query, data)
        conn.commit()
        stop_connection(conn, cursor)
        return True
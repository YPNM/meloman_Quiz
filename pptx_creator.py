from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
from pptx.enum.dml import MSO_THEME_COLOR_INDEX
from pptx.enum.text import PP_PARAGRAPH_ALIGNMENT
import db_init


def iter_cells(table):
    for row in table.rows:
        for cell in row.cells:
            yield cell


def create_powerpoint_with_table(folder, game_id):
    # Создаем новую презентацию

    teamsInGame = db_init.TeamsInGame()
    scoresModel = db_init.ScoresDB()
    roundsModel = db_init.RoundsDB()
    scoresDictionary = {}

    teams = teamsInGame.get_all_teams_in_game(game_id, active=True)
    allscores = scoresModel.get_scores_by_game_id(game_id=game_id)
    rounds = roundsModel.get_all_rounds(game_id=game_id)

    # template
    for round in rounds:
        for score in allscores:
            if (score[4] not in scoresDictionary.keys()):
                scoresDictionary[score[4]] = {'total': 0, 'items': []}
            if (round[0] == score[0]):
                scoresDictionary[score[4]]['total'] += score[3]
                scoresDictionary[score[4]]['items'].append(score)

    # find empty rounds
    maxRounds = 0
    # find empty rounds
    for key, value in scoresDictionary.items():
        if (len(value['items']) < len(rounds)):
            existRounds = []
            team_id = ''
            for item in value['items']:
                existRounds.append(item[0])
                team_id = item[2]
            for round in rounds:
                if (round[0] not in existRounds):
                    value['items'].append([round[0], round[1], team_id, 0, key])
            maxRounds = len(existRounds)

    # sorting by ascending order
    sortedDict = dict(sorted(scoresDictionary.items(), key=lambda x: x[1]['total'], reverse=True))

    if (maxRounds > 3):
        submitDict = {}
        temp = {
            'max': 0,
            'key': '',
        }
        for key, value in sortedDict.items():
            if (key not in submitDict.keys()):
                if (value['total'] == temp['max']):
                    length = len(value['items']) - 1
                    secondLength = len(sortedDict[key]['items']) - 1
                    while length != -1:
                        if value['items'][length][3] > scoresDictionary[temp['key']]['items'][secondLength][3]:
                            res = dict()
                            for secondKey in submitDict.keys():
                                if (secondKey == temp['key']):
                                    res[key] = {
                                        'total': value['total'],
                                        'items': value['items']
                                    }

                                res[secondKey] = submitDict[secondKey]
                            submitDict = res
                            length = -1
                        elif (value['items'][length][3] == scoresDictionary[temp['key']]['items'][secondLength][3]):
                            if (length == 0 and secondLength == 0):
                                submitDict[key] = {
                                    'total': value['total'],
                                    'items': value['items']
                                }
                                length = -1
                            else:
                                length -= 1
                                secondLength -= 1
                            continue
                        elif (value['items'][length][3] < scoresDictionary[temp['key']]['items'][secondLength][3]):
                            submitDict[key] = {
                                'total': value['total'],
                                'items': value['items']
                            }
                            length = -1
                else:
                    temp['max'] = value['total']
                    temp['key'] = key
                    submitDict[key] = {
                        'total': value['total'],
                        'items': value['items']
                    }
    else:
        submitDict = sortedDict
    # add new teams without scores
    for team in teams:
        if (team[3] not in submitDict.keys()):
            submitDict[team[3]] = {
                'total': None,
                'id': team[1]
            }

    prs = Presentation()
    game_result = {}

    for key, value in submitDict.items():
        game_result[key] = []
        for i in range(0, len(value['items'])):
            arr = value['items'][i]
            arr.append(value['total'])
            game_result[key].append(arr)


    rows = len(game_result.keys()) + 1
    cols = len(game_result.get(next(iter(game_result.keys())))) + 3
    table_length = Inches(4) + Inches(1) + (cols - 2) * Inches(0.7)

    # Добавляем слайд с таблицей
    slide_layout = prs.slide_layouts[5]  # 5 - это слайд с черным фоном
    slide = prs.slides.add_slide(slide_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0, 0, 0)  # Черный цвет фона
    # Определяем размеры слайда 16:9
    slide_width = Inches(16)  # 10 дюймов
    slide_height = Inches(9)  # 5.67 дюйма

    # Устанавливаем размеры слайда
    prs.slide_width = slide_width
    prs.slide_height = slide_height
    table = slide.shapes.add_table(rows=rows, cols=cols, left=Inches(16 / 2) - table_length / 2, top=Inches((9 / 2) - (rows * 0.5 / 2)),
                                   width=Inches(9),
                                   height=Inches(0.5) * rows)

    for cell in iter_cells(table.table):
        fill = cell.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0, 0, 0)

    counter = 1
    comands = list(game_result.keys())
    for i in range(rows):
        for j in range(cols):
            cell = table.table.cell(i, j)
            if i == 0:
                if j == 0:
                    cell.text = "№"
                elif j == 1:
                    cell.text = "Название команды"
                elif j == cols - 1:
                    cell.text = "Всего"
                else:
                    cell.text = str(counter)
                    counter += 1
            else:
                for paragraph in cell.text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.font.color.rgb = RGBColor(255, 255, 255)  # Белый цвет текста
                if j == 0:
                    cell.text = str(i)
                elif j == 1:
                    cell.text = str(comands[i - 1])
                elif j == cols - 1:
                    cell.text = str(float(game_result.get(comands[i - 1])[0][5]))
                else:
                    cell.text = str(game_result.get(comands[i - 1])[j - 2][3])
                cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
            cell.text_frame.paragraphs[0].font.size = Pt(22)
            cell.text_frame.paragraphs[0].font.bold = True

    for i in range(cols):
        if i == 1:
            table.table.columns[i].width = Inches(4)
        elif i == cols - 1:
            table.table.columns[i].width = Inches(1)
        else:
            table.table.columns[i].width = Inches(0.7)
    path = f'{folder}/table.pptx'
    # Сохраняем презентацию
    prs.save(path)
    return path
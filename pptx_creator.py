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


def create_powerpoint_with_table(game_id):
    # Создаем новую презентацию
    prs = Presentation()
    result_model = db_init.ScoresDB()
    game_result = result_model.get_scores_by_game_id(game_id)
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
                    cell.text = str(float(game_result.get(comands[i - 1])[0][4]))
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

    # Сохраняем презентацию
    prs.save("Таблица.pptx")


# Используем функцию для создания презентации
create_powerpoint_with_table("05eba41b-4925-11ee-8a2c-6c2408aface6")

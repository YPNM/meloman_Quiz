// Получаем ссылки на радио-кнопки и таблицы
const gameRadio = document.getElementById('game');
const seasonRadio = document.getElementById('season');
const gameTable = document.querySelector('.game-table');
const seasonTable = document.querySelector('.season-table');

// Добавляем обработчики событий на радио-кнопки
gameRadio.addEventListener('change', () => {
  gameTable.style.display = 'block';
  seasonTable.style.display = 'none';
});

seasonRadio.addEventListener('change', () => {
  gameTable.style.display = 'none';
  seasonTable.style.display = 'block';
});

// Изначально скрываем одну из таблиц
gameTable.style.display = 'block'; // или 'none', в зависимости от того, какую хотите показать по умолчанию
seasonTable.style.display = 'none'; // или 'block'

// Получаем ссылки на радио-кнопки и таблицы
const gameRadio = document.getElementById('game');
const seasonRadio = document.getElementById('season');
const gameButton = document.getElementById('game-selector');
const gameTable = document.querySelector('.game-table');
const seasonTable = document.querySelector('.season-table');

// Добавляем обработчики событий на радио-кнопки
gameRadio.addEventListener('change', () => {
  gameTable.style.display = 'block';
  seasonTable.style.display = 'none';
  gameButton.style.display = 'inline-block';
});

seasonRadio.addEventListener('change', () => {
  gameTable.style.display = 'none';
  seasonTable.style.display = 'block';
  gameButton.style.display = 'none';
});

// Изначально скрываем одну из таблиц
gameButton.style.display = 'none';
gameTable.style.display = 'none'; // или 'none', в зависимости от того, какую хотите показать по умолчанию
seasonTable.style.display = 'block'; // или 'block'

function toggleCard(card) {
    card.classList.toggle('selected');
    showPopup();
  }

  function showPopup() {
    const popupContainer = document.getElementById('popup-container');
    popupContainer.style.display = 'flex';
  }

  function closePopup() {
    const popupContainer = document.getElementById('popup-container');
    popupContainer.style.display = 'none';

    // Убрать класс selected у всех карточек при закрытии всплывающего окна
    const cards = document.querySelectorAll('.first_ticket');
    cards.forEach(card => {
      card.classList.remove('selected');
    });
  }


  function cancelFlight() {
    alert('Рейс отменен');
    closePopup();
  }

  function delayFlight() {
    alert('Рейс задержан');
    closePopup();
  }

  function logout() {
    // Ваша логика для выхода с аккаунта
    alert('Вы успешно вышли с аккаунта');
    closePopup();
  }


  // Получить все элементы с классом "first_ticket"
const tickets = document.querySelectorAll('.first_ticket');

// Функция для выполнения поиска
function searchTickets() {
  // Получить значение из input
  const searchText = document.querySelector('.search_ticket input').value.toLowerCase();

  // Перебрать все билеты и скрыть те, которые не соответствуют поисковому запросу
  tickets.forEach(ticket => {
    const ticketText = ticket.textContent.toLowerCase();
    if (ticketText.includes(searchText)) {
      ticket.style.display = 'flex'; // Показать билет, если соответствует
    } else {
      ticket.style.display = 'none'; // Скрыть билет, если не соответствует
    }
  });
}

// Добавить обработчик события на изменение input
document.querySelector('.search_ticket input').addEventListener('input', searchTickets);

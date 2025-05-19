// S: Single Responsibility — Cada función tiene una única responsabilidad clara.
// O: Open/Closed — Usamos data attributes para que sea fácilmente extendible sin cambiar funciones.

// ModalController gestiona la apertura y cierre de modales
const ModalController = (() => {
    function open(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    function close(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    function closeAllOnOutsideClick(event) {
        document.querySelectorAll('.modal').forEach(modal => {
            if (event.target === modal) close(modal.id);
        });
    }

    return {
        open,
        close,
        closeAllOnOutsideClick
    };
})();

// VoteController gestiona la votación para publicaciones y comentarios
const VoteController = (() => {
    function initVoteButtons(selector, upClass, downClass, countSelector, formatter = n => n) {
        document.querySelectorAll(selector).forEach(button => {
            button.addEventListener('click', function () {
                const container = this.closest('[data-votable]');
                const countElement = container.querySelector(countSelector);
                let count = parseInt(countElement.textContent.replace(/[^\d.-]/g, '')) || 0;

                if (this.classList.contains(upClass)) {
                    count += 1;
                } else if (this.classList.contains(downClass)) {
                    count -= 1;
                }

                countElement.textContent = formatter(count);
            });
        });
    }

    function formatCount(num) {
        return num >= 1000 ? (num / 1000).toFixed(1) + 'k' : num.toString();
    }

    return {
        init: () => {
            initVoteButtons('.post__vote-button', 'post__vote-button--up', 'post__vote-button--down', '.post__vote-count', formatCount);
            initVoteButtons('.comment__vote-button', 'comment__vote-button--up', 'comment__vote-button--down', '.comment__vote-count');
        }
    };
})();

// CommentController gestiona la lógica de comentarios
const CommentController = (() => {
    function init() {
        const button = document.querySelector('.comment-form__button');
        const textarea = document.querySelector('.comment-form__textarea');

        if (!button || !textarea) return;

        button.addEventListener('click', () => {
            const commentText = textarea.value.trim();
            if (commentText) {
                alert('Comentario enviado: ' + commentText);
                textarea.value = '';
                // Aquí agregar lógica real con DOM y backend si aplica
            } else {
                alert('Por favor escribe un comentario');
            }
        });
    }

    return { init };
})();

// SearchController gestiona el input de búsqueda
const SearchController = (() => {
    function init() {
        const input = document.getElementById('searchInput');
        if (!input) return;

        input.addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                const value = input.value.trim();
                if (value) alert('Buscando: ' + value);
            }
        });
    }

    return { init };
})();

// Inicializar toda la app (cumpliendo SRP al delegar a cada módulo)
document.addEventListener('DOMContentLoaded', () => {
    VoteController.init();
    CommentController.init();
    SearchController.init();

    // Eventos para abrir modales
    document.querySelectorAll('[data-open-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            ModalController.open(btn.dataset.openModal);
        });
    });

    // Eventos para cerrar modales
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            ModalController.close(btn.dataset.closeModal);
        });
    });

    // Cierre al hacer clic fuera del modal
    window.addEventListener('click', ModalController.closeAllOnOutsideClick);
});

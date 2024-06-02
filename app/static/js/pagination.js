document.addEventListener("DOMContentLoaded", function() {
    // Función para mostrar elementos con paginación
    function paginate(container, contentClass, prevButtonClass, nextButtonClass, itemsPerPage) {
        const contents = container.querySelectorAll(contentClass);
        let currentPage = 0;

        function showPage(page) {
            contents.forEach((content, index) => {
                content.classList.remove('active');
                if (index >= page * itemsPerPage && index < (page + 1) * itemsPerPage) {
                    content.classList.add('active');
                }
            });
            updateButtons();
        }

        function updateButtons() {
            container.querySelector(prevButtonClass).disabled = currentPage === 0;
            container.querySelector(nextButtonClass).disabled = currentPage === Math.ceil(contents.length / itemsPerPage) - 1;
        }

        container.querySelector(prevButtonClass).addEventListener('click', () => {
            if (currentPage > 0) {
                currentPage--;
                showPage(currentPage);
            }
        });

        container.querySelector(nextButtonClass).addEventListener('click', () => {
            if (currentPage < Math.ceil(contents.length / itemsPerPage) - 1) {
                currentPage++;
                showPage(currentPage);
            }
        });

        // Mostrar la primera página al cargar
        showPage(0);
    }

    // Paginar vídeos
    paginate(document.querySelector('.video-pagination'), '.video-content', '.video-prev', '.video-next', 1);

    // Paginar comentarios
    paginate(document.querySelector('.comment-pagination'), '.comment-content', '.comment-prev', '.comment-next', 2);
});

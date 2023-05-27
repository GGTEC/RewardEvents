
                const emojis = document.querySelectorAll('#emojis img');
                emojis.forEach((emoji) => {
                emoji.style.left = `calc(100% * ${Math.random()})`;
                });
            
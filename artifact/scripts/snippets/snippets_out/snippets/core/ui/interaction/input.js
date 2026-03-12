/**
 * Input Management
 */

export const InputManager = {
    setupInput(config) {
        const {
            input,
            submitButton,
            onSubmit,
            onKeyPress = true,
            clearOnSubmit = true,
            validation = (value) => value.trim() !== ''
        } = config;

        if (!input || !submitButton || !onSubmit) return;

        const handleSubmit = () => {
            const value = input.value;
            if (!validation(value)) return;

            onSubmit(value);
            if (clearOnSubmit) {
                input.value = '';
            }
        };

        submitButton.addEventListener('click', handleSubmit);

        if (onKeyPress) {
            input.addEventListener('keypress', (event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    handleSubmit();
                }
            });
        }

        return {
            clear: () => { input.value = ''; },
            getValue: () => input.value,
            setValue: (value) => { input.value = value; },
            focus: () => { input.focus(); }
        };
    }
}; 
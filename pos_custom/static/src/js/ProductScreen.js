odoo.define('pos_custom.ProductScreen', function(require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");

    const PosCustomProductScreen = ProductScreen => class extends ProductScreen {
        setup() {
            super.setup();
            useListener('click-car', this.onClickCar);
        }

        async _clickProduct(event) {
            super._clickProduct(event)
            if (this.env.isMobile) {
                this.switchPane()
            }
        }

        async onClickCar() {
            const currentCar = this.currentOrder.get_car();
            const { confirmed, payload: newCar } = await this.showTempScreen(
                'CarListScreen',
                { car: currentCar }
            );
            if (confirmed) {
                this.currentOrder.set_car(newCar);
            }
        }

        async _onClickPay() {
            if (!this.currentOrder.get_car()) {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Car Missing'),
                    body: this.env._t(
                        'There must be a car selected to complete the order.'
                    ),
                });
                return;
            }
            super._onClickPay();
        }

    };

    Registries.Component.extend(ProductScreen, PosCustomProductScreen);

    return ProductScreen;
});

odoo.define('pos_custom.PaymentScreen', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { onMounted } = owl;

    const PosCustomPaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {
        super.setup();

            onMounted(() => {
                const default_method = this.payment_methods_from_config.find((element) => element.is_default)
                if (this.currentOrder.get_due() > 0){
                    this.addNewPaymentLine({detail:default_method})
                }
            });
        }
        async _finalizeValidation() {
            this.currentOrder.car = this.env.pos.get_order().get_car();
            await super._finalizeValidation();
        }
    };

    Registries.Component.extend(PaymentScreen, PosCustomPaymentScreen);

    return PaymentScreen;
});

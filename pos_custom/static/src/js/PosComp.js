odoo.define('pos_custom.PosComp', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    class PosComp extends PosComponent {
        get currentOrderCar() {
            var curentOrder = this.env.pos.get_order();
            if (curentOrder && curentOrder.car){
                return curentOrder.car.license
            }
            return false;
        }
    }


    PosComp.template = 'CarsButton';

    ProductScreen.addControlButton({
        component: PosComp,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(PosComp);

    return PosComp;
});
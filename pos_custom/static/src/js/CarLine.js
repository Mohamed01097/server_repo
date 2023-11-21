odoo.define('point_of_sale.CarLine', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class CarLine extends PosComponent {
        get highlight() {
            return this._isCarSelected ? 'highlight' : '';
        }
        get _isCarSelected() {
            return this.props.car === this.props.selectedCar;
        }
    }
    CarLine.template = 'CarLine';

    Registries.Component.add(CarLine);

    return CarLine;
});

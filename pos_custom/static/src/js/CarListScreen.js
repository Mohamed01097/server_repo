odoo.define('point_of_sale.CarListScreen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { isConnectionError } = require('point_of_sale.utils');

    const { debounce } = require("@web/core/utils/timing");
    const { useListener } = require("@web/core/utils/hooks");

    const { onWillUnmount, useRef } = owl;

    /**
     * Render this screen using `showTempScreen` to select car.
     * When the shown screen is confirmed ('Set Car' or 'Deselect Car'
     * button is clicked), the call to `showTempScreen` resolves to the
     * selected car. E.g.
     *
     * ```js
     * const { confirmed, payload: selectedCar } = await showTempScreen('CarListScreen');
     * if (confirmed) {
     *   // do something with the selectedCar
     * }
     * ```
     *
     * @props car - originally selected car
     */
    class CarListScreen extends PosComponent {
        setup() {
            super.setup();

            this.searchWordInputRef = useRef('search-word-input-car');

            // We are not using useState here because the object
            // passed to useState converts the object and its contents
            // to Observer proxy. Not sure of the side-effects of making
            // a persistent object, such as pos, into Observer. But it
            // is better to be safe.
            this.state = {
                query: null,
                selectedCar: this.props.car,
                detailIsShown: false,
                editModeProps: {
                    car: null,
                },
            };

            this.updateCarList = debounce(this.updateCarList, 70);
            onWillUnmount(this.updateCarList.cancel);
        }
        // Lifecycle hooks
        back() {
            if(this.state.detailIsShown) {
                this.state.detailIsShown = false;
                this.render(true);
            } else {
                this.props.resolve({ confirmed: false, payload: false });
                this.trigger('close-temp-screen');
            }
        }
        confirm() {
            this.props.resolve({ confirmed: true, payload: this.state.selectedCar, car: this.state.selectedCar });
            this.trigger('close-temp-screen');
        }
        
        // Getters

        get currentOrder() {
            return this.env.pos.get_order();
        }

        get cars() {
            let res;

            if (this.state.query && this.state.query.trim() !== '') {
                res = this.env.pos.db.search_car(this.state.query.trim());
            } else {
                res = this.env.pos.db.get_cars_sorted(1000);
            }

            res.sort(function (a, b) { return (a.name || '').localeCompare(b.name || '') });
            // the selected car (if any) is displayed at the top of the list
            if (this.state.selectedCar) {
                let indexOfSelectedCar = res.findIndex( car => 
                    car.id === this.state.selectedCar.id
                );
                if (indexOfSelectedCar !== -1) {
                    res.splice(indexOfSelectedCar, 1);
                    res.unshift(this.state.selectedCar);
                }
            }
            return res
        }


        clickCar(car) {
            if (this.state.selectedCar && this.state.selectedCar.id === car.id) {
                this.state.selectedCar = null;
            } else {
                this.state.selectedCar = car;
            }
            this.confirm();
        }

        // Methods
        async _onPressEnterKey() {
            if (!this.state.query) return;
            const result = await this.searchCar();
            this.showNotification(
                _.str.sprintf(
                    this.env._t('%s car(s) found for "%s".'),
                    result.length,
                    this.state.query
                ),
                3000
            );
        }
        _clearSearch() {
            this.searchWordInputRef.el.value = '';
            this.state.query = '';
            this.render(true);
        }
        // We declare this event handler as a debounce function in
        // order to lower its trigger rate.
        async updateCarList(event) {
            this.state.query = event.target.value;
            if (event.code === 'Enter') {
                this._onPressEnterKey();
            } else {
                this.render(true);
            }
        }
        async searchCar() {
            let result = await this.getNewCars();
            this.env.pos.addCars(result);
            this.render(true);
            return result;
        }
        async getNewCars() {
            let domain = [];
            if(this.state.query) {
                domain = [["name", "ilike", this.state.query + "%"]];
            }
            const result = await this.env.services.rpc(
                {
                    model: 'pos.session',
                    method: 'get_pos_ui_vendor_truck_by_params',
                    args: [
                        [odoo.pos_session_id],
                        {
                            domain,
                            limit: 10,
                        },
                    ],
                    context: this.env.session.user_context,
                },
                {
                    timeout: 3000,
                    shadow: true,
                }
            );
            return result;
        }
    }
    CarListScreen.template = 'CarListScreen';

    Registries.Component.add(CarListScreen);

    return CarListScreen;
});

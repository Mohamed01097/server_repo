odoo.define('pos_custom.models', function (require) {
    "use strict";
    
    const { Order, PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    
    const CustomOrder = (Order) => class CustomOrder extends Order {
        constructor() {
            super(...arguments);
            this.to_invoice = true;
            this.car = this.car || null;
            this.car_driver = this.car_driver || '';

        }
        
        set_partner(partner){
            super.set_partner(partner);
            if (partner && partner.is_combined_invoice){
                this.to_invoice = false
            } else {
                this.to_invoice = true
            }
        }

        set_car(car){
            this.assert_editable();
            if (car) {
                this.car = car;
                this.car_driver = car[['license']];
            }
            else {
                this.car = null;
                this.car_driver = '';
            }
        }

        get_car(){
            return this.car;
        }

        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.car_id = this.car ? this.car : null;
            return json;
        }

        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            let car;
            if (json.car_id) {
                car = json.car_id;
                this.set_car(car);
            } else {
                car = null;
            }
        }
    }
    Registries.Model.extend(Order, CustomOrder)
    

    const CustomPosGlobalState = (PosGlobalState) => class CustomPosGlobalState extends PosGlobalState {
        constructor() {
            super(...arguments);
            this.cars = [];
        }

        async loadPartnersBackground(domain=[], offset=0, order=false) {
            // Start at the first page since the first set of loaded partners are not actually in the
            // same order as this background loading procedure.
            let i = 0;
            let partners = [];
            do {
                partners = await this.env.services.rpc({
                    model: 'pos.session',
                    method: 'get_pos_ui_res_partner_by_params',
                    args: [
                        [odoo.pos_session_id],
                        {
                            domain: [['customer_rank', '>', 0]],
                            limit: this.config.limited_partners_amount,
                            offset: offset + this.config.limited_partners_amount * i,
                            order: order,
                        },
                    ],
                    context: this.env.session.user_context,
                }, { shadow: true });
                this.addPartners(partners);
                i += 1;
            } while(partners.length);
        }

        async _processData(loadedData) {
            await super._processData(...arguments);
            this.cars = loadedData['vendor.truck'];
            this.car_by_id = loadedData['car_by_id'];
            this.addCars(this.cars);
        }

        get_cars(){
            return this.cars;
        }
        
        addCars(cars) {
            return this.db.add_cars(cars);
        }

        // load the cars based on the ids
        async _loadCars(carIds) {
            if (carIds.length > 0) {
                var domain = [['id','in', carIds]];
                const fetchedCars = await this.env.services.rpc({
                    model: 'pos.session',
                    method: 'get_pos_ui_vendor_truck_by_params',
                    args: [[odoo.pos_session_id], {domain}],
                }, {
                    timeout: 3000,
                    shadow: true,
                });
                this.addCars(fetchedCars);
            }
    }
    }
    Registries.Model.extend(PosGlobalState, CustomPosGlobalState);
    
});
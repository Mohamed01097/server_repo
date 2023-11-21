odoo.define('pos_custom.ClosePosPopup', function (require) {
    'use strict';

    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');

    const CustomClosePopup = (ClosePosPopup) =>
        class extends ClosePosPopup {
            setup() {
                super.setup();
                this.selectedCarReport = this.env.pos.get_cars();
            }

            async downloadCarReport() {
                var selected_value = document.querySelector('#selected_car').value;
                var carReportId
                var carList = []
                if (selected_value == 'All') {
                    this.selectedCarReport = this.env.pos.get_cars();
                    var json_object = JSON.parse(JSON.stringify(this.selectedCarReport))

                    for (let i=0; i < json_object.length; i++) {
                        carList.push(json_object[i]['id'])
                    }
                    carReportId = await this.env.services.rpc({
                        model: 'pos.session.car',
                        method: 'create',
                        args: [{'session_id': this.env.pos.pos_session.id, 'car_ids': carList}],
                    })
                } else {
                    this.selectedCarReport = selected_value
                    carList.push(parseInt(this.selectedCarReport))
                    carReportId = await this.env.services.rpc({
                        model: 'pos.session.car',
                        method: 'create',
                        args: [{'session_id': this.env.pos.pos_session.id, 'car_ids': carList}],
                    })
                };
                var isCarsPresent = await this.env.services.rpc({
                    model: 'pos.session.car',
                    method: 'check_if_car_has_order_for_pos',
                    args: [carReportId],
                })
                if (!isCarsPresent) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Change Selected Cars'),
                        body: this.env._t(
                            'Selected Cars do not have any Orders please choose another Car.'
                        ),
                    });
                    return;
                }
                await this.env.legacyActionManager.do_action('pos_custom.eos_car_report', {
                    additional_context: {
                        active_ids: [carReportId],
                    },
                });
            }

        };

    Registries.Component.extend(ClosePosPopup, CustomClosePopup);

    return ClosePosPopup;
});

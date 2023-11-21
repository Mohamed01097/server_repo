odoo.define('pos_custom.db', function (require) {
    'use strict';

    const PosDB = require('point_of_sale.DB');
    var utils = require('web.utils');
    PosDB.include({
        init: function(options){
            this._super(options);
            this.car_sorted = [];
            this.car_by_id = {};
            this.car_write_date = null;
            this.car_search_strings = {};
        },

        _car_search_string: function(car){
            var str =  car.name || '';
            // if(partner.barcode){
            //     str += '|' + partner.barcode;
            // }
            // if(partner.address){
            //     str += '|' + partner.address;
            // }
            // if(partner.phone){
            //     str += '|' + partner.phone.split(' ').join('');
            // }
            // if(partner.mobile){
            //     str += '|' + partner.mobile.split(' ').join('');
            // }
            // if(partner.email){
            //     str += '|' + partner.email;
            // }
            // if(partner.vat){
            //     str += '|' + partner.vat;
            // }
            // if(partner.parent_name){
            //     str += '|' + partner.parent_name;
            // }
            str = '' + car.id + ':' + str.replace(':', '').replace(/\n/g, ' ') + '\n';
            return str;
        },

        add_cars: function(cars){
            var updated = {};
            var new_write_date = '';
            var car;
            for(var i = 0, len = cars.length; i < len; i++){
                car = cars[i];
    
                var local_car_date = (this.car_write_date || '').replace(/^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/, '$1T$2Z');
                var dist_car_date = (car.car_write_date || '').replace(/^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/, '$1T$2Z');
                if (    this.car_write_date &&
                        this.car_by_id[car.id] &&
                        new Date(local_car_date).getTime() + 1000 >=
                        new Date(dist_car_date).getTime() ) {
                    continue;
                } else if ( new_write_date < car.write_date ) {
                    new_write_date  = car.write_date;
                }
                if (!this.car_by_id[car.id]) {
                    this.car_sorted.push(car.id);
                }
                updated[car.id] = car;
                this.car_by_id[car.id] = car;
            }
    
            this.car_write_date = new_write_date || this.car_write_date;

            const updatedChunks = new Set();
            const CHUNK_SIZE = 100;
            for (const id in updated) {
                const chunkId = Math.floor(id / CHUNK_SIZE);
                if (updatedChunks.has(chunkId)) {
                    // another car in this chunk was updated and we already rebuild the chunk
                    continue;
                }
                updatedChunks.add(chunkId);
                // If there were updates, we need to rebuild the search string for this chunk
                let searchString = "";
    
                for (let id = chunkId * CHUNK_SIZE; id < (chunkId + 1) * CHUNK_SIZE; id++) {
                    if (!(id in this.car_by_id)) {
                        continue;
                    }
                    const car = this.car_by_id[id];
                    searchString += this._car_search_string(car);
                }
    
                this.car_search_strings[chunkId] = utils.unaccent(searchString);
            }
    
            return Object.keys(updated).length;
        },

        search_car: function(query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(/ /g,'.+');
                var re = RegExp("([0-9]+):.*?"+utils.unaccent(query),"gi");
            }catch(_e){
                return [];
            }
            var results = [];
            const searchStrings = Object.values(this.car_search_strings).reverse();
            let searchString = searchStrings.pop();
            while (searchString && results.length < this.limit) {
                var r = re.exec(searchString);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_car_by_id(id));
                } else {
                    searchString = searchStrings.pop();
                }
            }
            return results;
        },


        get_car_by_id: function(id){
            return this.car_by_id[id];
        },
        
        get_cars_sorted: function(max_count){
            max_count = max_count ? Math.min(this.car_sorted.length, max_count) : this.car_sorted.length;
            var cars = [];
            for (var i = 0; i < max_count; i++) {
                cars.push(this.car_by_id[this.car_sorted[i]]);
            }
            return cars;
        },

    });
});
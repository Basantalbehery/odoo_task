import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class EquipmentDashboard extends Component {
    static template = "porcelia_equipment_loan.EquipmentDashboard";

    setup() {

        this.orm = useService("orm");
        this.action = useService("action");


        this.state = useState({
            period: "month",
            data: null,
            loading: true,
        });


        onWillStart(async () => {
            await this.loadData();
        });
    }


    async loadData() {
        this.state.loading = true;
        const data = await this.orm.call("equipment.loan", "get_dashboard_data", [this.state.period]);
        this.state.data = data;
        this.state.loading = false;
    }


    async setPeriod(period) {
        if (this.state.period !== period) {
            this.state.period = period;
            await this.loadData();
        }
    }


    openLoan(loanId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "equipment.loan",
            res_id: loanId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}


registry.category("actions").add("equipment_dashboard", EquipmentDashboard);
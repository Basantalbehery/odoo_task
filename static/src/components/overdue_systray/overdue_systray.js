import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class OverdueSystray extends Component {
    static template = "porcelia_equipment_loan.OverdueSystray";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ overdueCount: 0 });

        onWillStart(async () => {
            await this.fetchOverdueCount();
        });
    }

    async fetchOverdueCount() {
        const today = new Date().toISOString().slice(0, 19).replace('T', ' ');
        const count = await this.orm.searchCount("equipment.loan", [
            ["state", "=", "confirmed"],
            ["date_due", "<", today]
        ]);
        this.state.overdueCount = count;
    }

    async onClick() {
        const today = new Date().toISOString().slice(0, 19).replace('T', ' ');
        await this.action.doAction({
            name: "Overdue Loans",
            type: "ir.actions.act_window",
            res_model: "equipment.loan",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "=", "confirmed"], ["date_due", "<", today]],
            target: "current",
        });
    }
}

export const overdueSystrayItem = {
    Component: OverdueSystray,
};

registry.category("systray").add("OverdueSystray", overdueSystrayItem, { sequence: 10 });
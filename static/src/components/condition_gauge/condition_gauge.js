import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class ConditionGaugeField extends Component {
    static template = "porcelia_equipment_loan.ConditionGaugeField";
    static props = {
        ...standardFieldProps,
        segments: { type: Number, optional: true },
    };
    static defaultProps = {
        segments: 10,
    };

    get rawValue() {
        return this.props.record.data[this.props.name] || 0;
    }

    get score() {
        return Math.max(0, Math.min(100, this.rawValue));
    }

    get segments() {
        return this.props.segments || 10;
    }

    get segment_array() {
        return Array.from({ length: this.segments }, (_, i) => i);
    }

    get gaugeColorClass() {
        const val = this.score;
        if (val < 40) return "bg-danger";
        if (val < 75) return "bg-warning";
        return "bg-success";
    }

    get activeSegmentCount() {
        return Math.round((this.score / 100) * this.segments);
    }

    async onSegmentClick(index) {
        if (this.props.readonly) return;
        const newValue = Math.round(((index + 1) / this.segments) * 100);
        await this.props.record.update({ [this.props.name]: newValue });
    }
}

export const conditionGaugeField = {
    component: ConditionGaugeField,
    supportedTypes: ["integer"],
    extractProps: ({ options }) => ({
        segments: options.segments ? parseInt(options.segments, 10) : 10,
    }),
};

registry.category("fields").add("condition_gauge", conditionGaugeField);
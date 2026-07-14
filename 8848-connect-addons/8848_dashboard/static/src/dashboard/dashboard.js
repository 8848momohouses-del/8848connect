/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { serializeDateTime } from "@web/core/l10n/dates";
import { user } from "@web/core/user";

const { DateTime } = luxon;

const OPEN_PICKING_STATES = ["confirmed", "waiting", "assigned"];

export class Dashboard8848 extends Component {
    static template = "8848_dashboard.Dashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ kpis: {} });
        this.userName = user.name;

        const now = DateTime.now();
        const monthStart = serializeDateTime(now.startOf("month"));
        const nowStr = serializeDateTime(now);

        this.cards = [
            {
                id: "crm",
                name: "CRM",
                icon: "fa-bullseye",
                className: "o_8848_card_crm",
                actionXmlId: "crm.crm_lead_action_pipeline",
                kpis: [
                    {
                        label: "In Pipeline",
                        model: "crm.lead",
                        domain: [["type", "=", "opportunity"]],
                    },
                    {
                        label: "Won This Month",
                        model: "crm.lead",
                        domain: [
                            ["stage_id.is_won", "=", true],
                            ["date_closed", ">=", monthStart],
                        ],
                    },
                ],
            },
            {
                id: "sales",
                name: "Sales",
                icon: "fa-line-chart",
                className: "o_8848_card_sales",
                actionXmlId: "sale.action_quotations_with_onboarding",
                kpis: [
                    {
                        label: "Quotations",
                        model: "sale.order",
                        domain: [["state", "in", ["draft", "sent"]]],
                    },
                    {
                        label: "To Invoice",
                        model: "sale.order",
                        domain: [["invoice_status", "=", "to invoice"]],
                    },
                ],
            },
            {
                id: "projects",
                name: "Projects",
                icon: "fa-tasks",
                className: "o_8848_card_projects",
                actionXmlId: "project.open_view_project_all",
                kpis: [
                    {
                        label: "Open Tasks",
                        model: "project.task",
                        domain: [["is_closed", "=", false]],
                    },
                    {
                        label: "Overdue",
                        model: "project.task",
                        domain: [
                            ["is_closed", "=", false],
                            ["date_deadline", "<", nowStr],
                        ],
                    },
                ],
            },
            {
                id: "inventory",
                name: "Inventory",
                icon: "fa-cubes",
                className: "o_8848_card_inventory",
                actionXmlId: "stock.action_picking_tree_all",
                kpis: [
                    {
                        label: "To Deliver",
                        model: "stock.picking",
                        domain: [
                            ["picking_type_code", "=", "outgoing"],
                            ["state", "in", OPEN_PICKING_STATES],
                        ],
                    },
                    {
                        label: "To Receive",
                        model: "stock.picking",
                        domain: [
                            ["picking_type_code", "=", "incoming"],
                            ["state", "in", OPEN_PICKING_STATES],
                        ],
                    },
                ],
            },
        ];

        onWillStart(() => this.loadKpis());
    }

    async loadKpis() {
        await Promise.all(
            this.cards.map(async (card) => {
                const values = await Promise.all(
                    card.kpis.map((kpi) =>
                        this.orm
                            .searchCount(kpi.model, kpi.domain)
                            .catch(() => "–")
                    )
                );
                this.state.kpis[card.id] = values;
            })
        );
    }

    kpiValue(card, index) {
        const values = this.state.kpis[card.id];
        return values === undefined ? "…" : values[index];
    }

    get greeting() {
        const hour = DateTime.now().hour;
        if (hour < 12) {
            return "Good morning";
        }
        if (hour < 17) {
            return "Good afternoon";
        }
        return "Good evening";
    }

    get today() {
        return DateTime.now().toFormat("cccc, d LLLL yyyy");
    }

    openApp(card) {
        this.action.doAction(card.actionXmlId);
    }
}

registry.category("actions").add("8848_dashboard.dashboard", Dashboard8848);

def migrate(cr, version):
    """Adopt pre-existing communication channels before the owned seed data
    (data/communication_channel_data.xml) loads.

    Databases upgraded from earlier releases already hold channel rows that
    were historically seeded by 8848_crm demo data. Without adoption the new
    8848_communication.channel_* records collide with the unique-code
    constraint and abort the upgrade (this took production down on
    2026-07-20). Assigning the new external IDs to the existing rows turns
    the seed load into a no-op update; removing the old 8848_crm external
    IDs stops CRM's data GC from deleting the adopted rows.
    """
    cr.execute("SELECT id, code FROM connect_communication_channel")
    for rec_id, code in cr.fetchall():
        cr.execute(
            """
            INSERT INTO ir_model_data (module, name, model, res_id, noupdate)
            SELECT '8848_communication', 'channel_' || %s,
                   '8848.communication.channel', %s, true
            WHERE NOT EXISTS (
                SELECT 1 FROM ir_model_data
                WHERE module = '8848_communication'
                  AND name = 'channel_' || %s
            )
            """,
            (code, rec_id, code),
        )
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE module = '8848_crm'
          AND model = '8848.communication.channel'
          AND name IN ('comm_channel_email', 'comm_channel_internal')
        """
    )

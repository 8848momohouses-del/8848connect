from . import models


def _assign_stage_to_existing_franchises(env):
    """Existing franchisees predate the lifecycle: they are operating stores,
    so place them at the 'Active Franchise' stage. Additive and reversible
    (the column is nullable); no data is modified beyond the empty stage."""
    stage = env.ref('8848_franchise.stage_active_franchise',
                    raise_if_not_found=False)
    if stage:
        env['res.partner'].search([
            ('is_franchise', '=', True),
            ('franchise_stage_id', '=', False),
        ]).write({'franchise_stage_id': stage.id})

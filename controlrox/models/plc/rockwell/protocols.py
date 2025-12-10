from controlrox.models.plc.protocols import HasRoutines

from .meta import RaPlcObject, PLC_ROUT_FILE


class RaHasRoutines(
    HasRoutines,
    RaPlcObject
):
    """Rockwell implementation of HasRoutines protocol.
    """

    default_l5x_file_path = PLC_ROUT_FILE
    default_l5x_asset_key = 'AddOnInstructionDefinition'

    @property
    def raw_routines(self) -> list[dict]:
        return self.get_raw_routines()

    def compile_routines(self):
        """compile the routines in this container

        This method compiles the routines from the raw metadata and initializes the HashList.
        """
        if self.controller is None:
            raise ValueError("Controller is not set for this object.")

        self._routines.clear()
        for routine in self.raw_routines:
            self._routines.append(
                self.controller.create_routine(
                    meta_data=routine,
                    controller=self.controller,
                    container=self  # type: ignore
                )
            )

    def get_raw_routines(self) -> list[dict]:
        """Get the raw routines metadata.

        Returns:
            list[dict]: List of raw routine metadata dictionaries.
        """
        meta_data = self.get_meta_data()
        if not isinstance(meta_data, dict):
            raise TypeError("Meta data must be a dictionary!")

        if not meta_data['Routines']:
            meta_data['Routines'] = {'Routine': []}
        if not isinstance(meta_data['Routines']['Routine'], list):
            meta_data['Routines']['Routine'] = [meta_data['Routines']['Routine']]
        return meta_data['Routines']['Routine']

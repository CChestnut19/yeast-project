import os
import uuid
from pathlib import Path

from .AssemblyFunction import Caculate
from Entity.Part import GetPartByName
from .WebDatabaseAssemblyClient import (
    AssemblyAPIError,
    WebDatabaseAssemblyClient,
)


class WebAssembly:
    def __init__(
        self,
        LBD,
        DBD,
        L,
        api_url,
        session,
        api_client = None,
        output_path = None,
    ):
        self.api_client = api_client or WebDatabaseAssemblyClient.from_env(
            session_factory=lambda: session, base_url=api_url,
        )
        self.api_url = self.api_client.base_url
        self.session = self.api_client.session
        self.lbd_name = LBD
        self.dbd_name = DBD
        missing = [
            name for name in ("Level2_Backbone_Name", "Level3_Backbone_Name")
            if not os.getenv(name)
        ]
        if missing:
            raise AssemblyAPIError(
                "TFPlot Assembly 配置错误：缺少 " + ", ".join(missing)
                + "。请在 TFPlot/.env 中设置对应的 Backbone 名称。"
            )
        self.Level2Backbone = os.getenv("Level2_Backbone_Name")
        self.Level3Backbone = os.getenv("Level3_Backbone_Name")
        self.L = L
        self.output_path = output_path or os.getenv("result_file")

    def CaculatePT(self):
        calculator = Caculate.Caculate(self.api_url, self.session,self.L)
        self.promoter, self.terminator = calculator.CaculateFunction()

    def AssemblyFunction(self):
        client = self.api_client
        client.login()
        self.LBD = GetPartByName(self.api_url, self.lbd_name, self.session)
        self.DBD = GetPartByName(self.api_url, self.dbd_name, self.session)
        self.AD = GetPartByName(self.api_url, "AD", self.session)
        if any(part is None for part in (self.LBD, self.DBD, self.AD)):
            raise AssemblyAPIError("Assembly requires existing LBD, DBD and AD parts")
        self.CaculatePT()
        part_names = [
            self.promoter.Name,
            f'{self.LBD.Name}',
            f'{self.DBD.Name}',
            f'{self.AD.Name}',
            self.terminator.Name,
        ]
        part_ids = [client.get_part_id(name) for name in part_names]

        request_uuid = str(uuid.uuid4())
        level2_name = f"Level2-{request_uuid}"
        level3_name = f"Level3-{request_uuid}"
        level2_payload = {
            "uuid": level2_name,
            "part": part_ids,
            "backbone": [self.Level2Backbone],
            "plasmid": [],
            "scar":[["",""],["aatg","tatc"],["tatc","ggta"],["ggta","taaa"],["",""]],
        }
        level2_task_id = client.submit_assembly(
            level2_payload, "Level2"
        )
        level2_result = client.wait_for_task(level2_task_id, "Level2")
        plasmid_id = level2_result.get("plasmid_id")
        if plasmid_id is None:
            raise AssemblyAPIError("Level2 completed without a persisted plasmid_id")
        level2_plasmid_name = client.get_plasmid_name(plasmid_id)

        level3_payload = {
            "uuid": level3_name,
            "part": [],
            "backbone": [self.Level3Backbone],
            # Use the actual stored name resolved from the result ID.
            "plasmid": [level2_plasmid_name],
        }
        level3_task_id = client.submit_assembly(
            level3_payload, "Level3"
        )
        level3_result = client.wait_for_task(
            level3_task_id, "Level3"
        )
        download_url = level3_result.get("download_url")
        if not isinstance(download_url, str) or not download_url:
            raise AssemblyAPIError("Level3 completed without a download_url")
        if self.output_path:
            destination = Path(self.output_path)
        else:
            import tempfile
            destination = Path(tempfile.gettempdir()) / "cic-designer" / f"{level3_name}.gb"
        file_path = client.download_result(download_url, destination)
        return {
            "success": True,
            "level2_plan_name": level2_name,
            "level2_task_id": level2_task_id,
            "level3_plan_name": level3_name,
            "level3_task_id": level3_task_id,
            "download_url": download_url,
            "file_path": file_path,
            "download_name": f"{level3_name}.gb",
        }

    def AssemblyFuntion(self):
        return self.AssemblyFunction()

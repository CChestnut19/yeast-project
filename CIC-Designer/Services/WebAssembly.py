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
        token = None,
    ):
        self.LBD = GetPartByName(api_url=api_url,Name=LBD,session = session)
        self.DBD = GetPartByName(api_url = api_url, Name=DBD, session=session)
        self.AD = GetPartByName(api_url = api_url,Name="AD",session = session)
        self.api_url = api_url
        self.session = session
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
        self.api_client = api_client
        self.output_path = output_path or os.getenv("result_file")
        self.token = token

    def CaculatePT(self):
        calculator = Caculate.Caculate(self.api_url, self.session,self.L)
        self.promoter, self.terminator = calculator.CaculateFunction()

    def AssemblyFunction(self):
        print(self.LBD)
        print(self.DBD)
        env_path = Path(__file__).resolve().parents[1] / ".env"
        client = self.api_client or WebDatabaseAssemblyClient(
            self.api_url, self.token
        )
        client.login()
        self.api_client = client
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
            "task_id": request_uuid,
        }
        level2_task_id = client.submit_assembly(
            level2_payload, "Level2"
        )
        print(level2_task_id)
        level2_result = client.wait_for_task(level2_task_id, "Level2")
        level2_assemblies = level2_result.get("assemblies") or []
        level2_plasmid_name = (
            level2_assemblies[0].get("plasmidName")
            if level2_assemblies else None
        )
        if not level2_plasmid_name:
            raise AssemblyAPIError(
                "Level2 completed without the persisted plasmid name"
            )

        level3_payload = {
            "uuid": level3_name,
            "part": [],
            "backbone": [self.Level3Backbone],
            # PlasmidNeed.Name is varchar(20); bio-app returns the actual
            # persisted (possibly truncated) name from the Level2 result.
            "plasmid": [level2_plasmid_name],
            "task_id": request_uuid,
        }
        level3_task_id = client.submit_assembly(
            level3_payload, "Level3"
        )
        level3_result = client.wait_for_task(
            level3_task_id, "Level3"
        )
        assemblies = level3_result.get("assemblies") or []
        download_file_id = assemblies[0].get("downloadFileId") if assemblies else None
        if not download_file_id:
            raise AssemblyAPIError(
                "Level3 completed without a download_url"
            )
        return {
            "success": True,
            "level2_plan_name": level2_name,
            "level2_task_id": level2_task_id,
            "level3_plan_name": level3_name,
            "level3_task_id": level3_task_id,
            "download_file_id": download_file_id,
        }

    def AssemblyFuntion(self):
        return self.AssemblyFunction()

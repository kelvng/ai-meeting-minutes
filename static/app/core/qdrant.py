from qdrant_client import QdrantClient as _QdrantClient
from ..config import settings


class QdrantClient:
    @staticmethod
    def connect():
        """
        Kết nối với QdrantClient
        """

        return _QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_APIKEY
        )

    @staticmethod
    def search(collection_name, query_vector, *, offset=0, limit=10, with_payload=True, payload_filter=None,
               score_threshold=0):
        """
        Tìm kiếm vector trong collection
        """

        try:
            client = QdrantClient.connect()

            if limit == 0:
                limit = client.count(collection_name).count

            if query_vector is None:
                score_threshold = 0

            search_params = {
                "collection_name": collection_name,
                "query_vector": query_vector,
                "limit": limit,
                "offset": offset,
                "score_threshold": score_threshold,
                "with_payload": with_payload,
            }
            if payload_filter is not None:
                must = []
                for key, value in payload_filter.items():
                    must.append({"key": key, "match": {"value": value}})
                search_params["query_filter"] = {"must": must}
            # print(search_params)
            results = client.search(**search_params)
            # print(results)
            return results
            # return results  [{"id": result.id, "score": result.score} for result in results]
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def search_groups(query_vector, group_by, collection_name, *, offset=0, limit=10, with_payload=True,
                      payload_filter=None, score_threshold=0):
        """
        Tìm kiếm vector theo group trong collection
        """

        try:
            client = QdrantClient.connect()

            if limit == 0:
                limit = client.count(collection_name).count

            if query_vector is None:
                score_threshold = 0

            search_params = {
                "collection_name": collection_name,
                "query_vector": query_vector,
                "limit": limit,
                "score_threshold": score_threshold,
                "with_payload": with_payload,
                "group_by": group_by
            }
            if payload_filter is not None:
                must = []
                for key, value in payload_filter.items():
                    must.append({"key": key, "match": {"value": value}})
                search_params["query_filter"] = {"must": must}
            # print(search_params)
            results = client.search_groups(**search_params)
            # print(results)
            return results
            # return results  [{"id": result.id, "score": result.score} for result in results]
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def upsert(collection_name, points):
        """
        Thêm hoặc cập nhật vector trong collection
        """

        try:
            client = QdrantClient.connect()
            response = client.upsert(
                collection_name=collection_name,
                wait=True,
                points=[points]
            )
            return {"success": response}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def create_collection(collection_name, vector_size, distance='Cosine'):
        """
        Tạo collection mới
        """
        from qdrant_client.models import Distance
        from qdrant_client.http.models import VectorParams

        try:
            client = QdrantClient.connect()

            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def delete_collection(collection_name):
        """
        Xóa collection
        """

        try:
            client = QdrantClient.connect()
            client.delete_collection(collection_name=collection_name)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_collection(collection_name):
        """
        Lấy thông tin của collection
        """

        try:
            client = QdrantClient.connect()
            return client.get_collection(collection_name=collection_name)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_collections():
        """
        Lấy danh sách tất cả các collection
        """

        try:
            client = QdrantClient.connect()
            return client.get_collections()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def delete(collection_name, points):
        """
        Xóa các point vectors khỏi collection
        """

        try:
            client = QdrantClient.connect()
            client.delete(collection_name=collection_name, points=points)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def retrieve(collection_name, ids):
        """
        Truy xuất các point vector theo ID
        """

        try:
            client = QdrantClient.connect()
            return client.retrieve(collection_name=collection_name, ids=ids)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def scroll(collection_name, offset=None, limit=10, with_payload=True):
        """
        Duyệt qua các point vector trong collection
        """

        try:
            client = QdrantClient.connect()
            return client.scroll(collection_name=collection_name, offset=offset, limit=limit, with_payload=with_payload)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def update_payload(collection_name, payload, points):
        """
        Cập nhật payload của các point vector
        """

        try:
            client = QdrantClient.connect()
            client.update_payload(collection_name=collection_name, payload=payload, points=points)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def delete_payload(collection_name, keys, points):
        """
        Xóa payload của các point vector
        """

        try:
            client = QdrantClient.connect()
            client.delete_payload(collection_name=collection_name, keys=keys, points=points)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def clear_payload(collection_name, points):
        """
        Xóa toàn bộ payload của các point vector
        """

        try:
            client = QdrantClient.connect()
            client.clear_payload(collection_name=collection_name, points=points)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def create_snapshot(collection_name):
        """
        Tạo snapshot của collection
        """

        try:
            client = QdrantClient.connect()
            return client.create_snapshot(collection_name=collection_name)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def list_snapshots(collection_name):
        """
        Liệt kê các snapshot của collection
        """

        try:
            client = QdrantClient.connect()
            return client.list_snapshots(collection_name=collection_name)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def delete_snapshot(collection_name, snapshot_name):
        """
        Xóa snapshot của collection
        """

        try:
            client = QdrantClient.connect()
            client.delete_snapshot(collection_name=collection_name, snapshot_name=snapshot_name)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def recover_from_snapshot(collection_name, snapshot_name):
        """
        Khôi phục collection từ snapshot
        """

        try:
            client = QdrantClient.connect()
            client.recover_from_snapshot(collection_name=collection_name, snapshot_name=snapshot_name)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def metrics():
        """
        Lấy các số liệu thống kê của Qdrant
        """

        try:
            client = QdrantClient.connect()
            return client.metrics()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def health():
        """
        Kiểm tra trạng thái của Qdrant
        """

        try:
            client = QdrantClient.connect()
            return client.health()
        except Exception as e:
            return {"error": str(e)}
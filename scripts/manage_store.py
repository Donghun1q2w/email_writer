"""
File Search Store 관리 CLI

사용법:
  python scripts/manage_store.py list-stores
  python scripts/manage_store.py create --name "my-store"
  python scripts/manage_store.py list-docs --store <name>
  python scripts/manage_store.py delete-doc --store <name> --doc <doc_name>
  python scripts/manage_store.py delete-store --store <name>
"""
import argparse

from email_writer.config import Settings
from email_writer.gemini.file_search import FileSearchManager


def main():
    parser = argparse.ArgumentParser(description="File Search Store 관리 도구")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-stores
    subparsers.add_parser("list-stores", help="File Search Store 목록 조회")

    # create
    create_parser = subparsers.add_parser("create", help="새 Store 생성")
    create_parser.add_argument("--name", required=True, help="Store 표시 이름")

    # list-docs
    list_docs_parser = subparsers.add_parser("list-docs", help="Store 내 문서 목록")
    list_docs_parser.add_argument("--store", required=True, help="Store 리소스 이름")

    # delete-doc
    del_doc_parser = subparsers.add_parser("delete-doc", help="문서 삭제")
    del_doc_parser.add_argument("--store", required=True, help="Store 리소스 이름")
    del_doc_parser.add_argument("--doc", required=True, help="삭제할 문서 이름")

    # delete-store
    del_store_parser = subparsers.add_parser("delete-store", help="Store 삭제")
    del_store_parser.add_argument("--store", required=True, help="삭제할 Store 리소스 이름")

    args = parser.parse_args()
    settings = Settings()
    manager = FileSearchManager(settings)

    if args.command == "list-stores":
        stores = manager.list_stores()
        for store in stores:
            print(f"  {store.name} ({store.display_name})")

    elif args.command == "create":
        store_name = manager.create_store(args.name)
        print(f"Store 생성 완료: {store_name}")
        print(f".env에 추가: EMAIL_WRITER_FILE_SEARCH_STORE_NAME={store_name}")

    elif args.command == "list-docs":
        docs = manager.list_documents(args.store)
        for doc in docs:
            print(f"  {doc.name}")

    elif args.command == "delete-doc":
        manager.delete_document(args.store, args.doc)
        print(f"문서 삭제 완료: {args.doc}")

    elif args.command == "delete-store":
        manager.delete_store(args.store)
        print(f"Store 삭제 완료: {args.store}")


if __name__ == "__main__":
    main()

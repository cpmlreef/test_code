# sub_functions/status_update.py
from typedb.driver import TypeDB, SessionType, TransactionType

def update_audit_status(audit_uuid, new_status, database_name="CodeDD_test_1", address=TypeDB.DEFAULT_ADDRESS):
    try:
        with TypeDB.core_driver(address) as driver:
            with driver.session(database_name, SessionType.DATA) as session:
                with session.transaction(TransactionType.WRITE) as tx:
                    try:
                        # Retrieve the current audit_status attribute
                        retrieve_query = f'match $audit isa audit, has audit_uuid "{audit_uuid}", has audit_status $status; get $status;'
                        answers = tx.query.match(retrieve_query)
                        current_status = next(answers, None)

                        # Delete the current audit_status if it exists
                        if current_status:
                            delete_query = f'match $audit isa audit, has audit_uuid "{audit_uuid}", has audit_status $status; delete $audit has $status;'
                            tx.query.delete(delete_query)

                        # Insert the new audit_status
                        insert_query = f'''
                        match $audit isa audit, has audit_uuid "{audit_uuid}";                                  
                        insert $audit isa audit, has audit_status "{new_status}";
                        '''
                        
                        tx.query.insert(insert_query)
                        tx.commit()
                        print(f"Audit status updated to '{new_status}'.")
                        return True
                    except Exception as e:
                        print(f"Failed to update audit status: {e}")
                        tx.rollback()
                        return False
    except Exception as e:
        print(f"Error connecting to TypeDB or during session: {e}")
        return False

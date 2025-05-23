/*
 * DBeaver - Universal Database Manager
 * Copyright (C) 2010-2024 DBeaver Corp and others
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.jkiss.dbeaver.ui;

import org.jkiss.dbeaver.DBException;
import org.jkiss.dbeaver.model.runtime.RunnableWithResult;
import org.jkiss.dbeaver.runtime.DBWorkbench;

public abstract class UITask<RESULT> extends RunnableWithResult<RESULT> {

    @Override
    public final RESULT runWithResult() throws DBException {
        return runTask();
    }

    protected abstract RESULT runTask() throws DBException;

    public RESULT execute() {
        return UIUtils.syncExec(this);
    }

    public interface TaskExecutor <T> {
        T run() throws DBException;
    }

    public static <T> T run(TaskExecutor <T> runnable) {
        return new UITask<T>() {
            @Override
            protected T runTask() {
                try {
                    return runnable.run();
                } catch (Exception e) {
                    DBWorkbench.getPlatformUI().showError("Task error", "Internal error: task " + runnable + "' failed", e);
                    return null;
                }
            }
        }.execute();
    }
}

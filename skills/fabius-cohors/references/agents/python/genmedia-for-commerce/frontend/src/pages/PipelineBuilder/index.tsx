/**
 * Copyright 2026 Google LLC
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

import TopNav from '../../components/TopNav'

function PipelineBuilder() {
  return (
    <div className="min-h-screen bg-gm-bg-light dark:bg-gm-bg flex flex-col">
      <TopNav />
      <div className="flex-1 relative">
        <iframe
          src="https://genmedia-pipes-demo-205784806851.us-central1.run.app/"
          className="w-full h-full absolute inset-0 border-0"
          title="Pipeline Builder"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        />
      </div>
    </div>
  )
}

export default PipelineBuilder

# -*- coding: utf-8 -*-
#
# Positronic Brain - Opinionated Buildbot Workflow
# Copyright (C) 2014  Develer S.r.L.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from buildbot.schedulers.forcesched import ForceScheduler, FixedParameter
from buildbot.steps.trigger import Trigger

from positronic.brain.config import BuildmasterConfig
from positronic.brain import utils
from positronic.brain.utils import scheduler_name


class Job(object):
    """The base class for all job types.

    It doesn't do much by itself, except for creating a new Builder and a new Force Scheduler so
    that users can forcibly trigger a new build.

    This class can be used as a context manager although, by default, it does nothing.

    """

    def __init__(self, name, workers):
        self.name = utils.name(name)
        self.workers = workers

        self.build = BuildFactory()

        BuildmasterConfig['builders'].append(BuilderConfig(
            name=self.name,
            factory=self.build,
            slavenames=self.workers))

        BuildmasterConfig['schedulers'].append(ForceScheduler(
            name=scheduler_name(self, 'force'),
            builderNames=[self.name],
            branch=FixedParameter(name="reason", default=""),
            reason=FixedParameter(name="reason", default="Forced build"),
            revision=FixedParameter(name="revision", default=""),
            repository=FixedParameter(name="repository", default=""),
            project=FixedParameter(name="project", default=""),
            properties=[],
            username=FixedParameter(name="username", default="WebUI")))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def add_step(self, step):
        """Adds a build step on this Job."""
        self.build.addStep(step)

    def trigger(self, job_or_jobs):
        """Adds a build step which triggers execution of another job."""
        if type(job_or_jobs) is list:
            self.add_step(Trigger(
                schedulerNames=[scheduler_name(j, 'trigger') for j in job_or_jobs],
                waitForFinish=True))
        else:
            self.add_step(Trigger(
                schedulerNames=[scheduler_name(job_or_jobs, 'trigger')],
                waitForFinish=True))